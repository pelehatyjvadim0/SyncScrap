import logging
from typing import Any

from root.shared.config import settings
from root.shared.rabbitmq import broker
from root.shared.queues import DOWNLOADED_PAGES, NORMALIZED_ITEMS
from root.shared.redis_client import RedisManager
from root.shared.schemas.pipeline_messages import ExtractionTask, HunterResult
from root.shared.schemas.raw_url_message import RawUrlMessage
from root.worker_downloader.logic.utils import DownloaderUtils
from root.worker_playwright.logic.browser.lifecycle import BrowserLifecycle
from root.worker_playwright.logic.message_payload import (
    RawUrlPayloadError,
    decode_raw_bytes,
    parse_raw_url_message,
)
from root.worker_playwright.logic.scenarios.registry import scenario_for_url

logger = logging.getLogger(__name__)


def _use_redis_cache(message: RawUrlMessage, cached_html: str | None) -> bool:
    if message.force_refresh:
        logger.debug(" [🎭] force_refresh=true — кеш Redis игнорируется")
        return False
    if cached_html is None:
        return False
    return True


class PlaywrightWorkflow:
    # Сообщение → сценарий Playwright → HTML в Redis → downloaded_pages.

    def __init__(self, browser: BrowserLifecycle, storage: RedisManager) -> None:
        self._browser = browser
        self._storage = storage

    async def run(self, msg: Any) -> None:
        raw = decode_raw_bytes(msg)
        logger.debug(" [🎭] Сырое тело raw_urls_playwright (первые 200): %.200s", raw)

        try:
            message = parse_raw_url_message(raw)
        except RawUrlPayloadError as exc:
            logger.warning(" [🎭] Отклонено сообщение: %s", exc)
            raise

        url = str(message.url)
        logger.info(" [→] URL (playwright): %s force_refresh=%s", url, message.force_refresh)

        redis_key = await DownloaderUtils.get_url_hash(url)
        cached_html = await self._storage.get_html(redis_key)

        if _use_redis_cache(message, cached_html):
            logger.info(" [↻] HTML из Redis, браузер не нужен. url=%s", url)
        else:
            await self._render_and_store(url, redis_key)

        await self._publish_downloaded(redis_key, url)

    async def run_extraction_task(self, task: ExtractionTask) -> None:
        url = str(task.listing.url)
        redis_key = await DownloaderUtils.get_url_hash(url)
        cached_html = await self._storage.get_html(redis_key)

        raw_message = RawUrlMessage(url=task.listing.url, force_refresh=task.force_refresh)
        if _use_redis_cache(raw_message, cached_html):
            logger.info(" [↻] HTML из Redis (extraction_task). url=%s", url)
        else:
            await self._render_and_store(url, redis_key)

        hunter_result = HunterResult(listing=task.listing, storage_key=redis_key)
        await broker.publish(
            message=hunter_result.model_dump(mode="json"),
            queue=NORMALIZED_ITEMS,
        )
        logger.info(" [✓] Hunter result queued for normalize. key=%s", redis_key)

    async def _render_and_store(self, url: str, redis_key: str) -> None:
        scenario = scenario_for_url(url)
        async with self._browser.page_session() as page:
            html = await scenario.run(page, url)

        try:
            await self._storage.set_html(
                key=redis_key,
                html=html,
                expire=settings.downloader.HTML_EXPIRE_SECONDS,
            )
        except Exception:
            logger.exception(
                " [🎭] Не удалось сохранить HTML в Redis. ключ=%s", redis_key
            )
            raise
        logger.info(" [✓] HTML (playwright) в Redis. url=%s ключ=%s", url, redis_key)

    async def _publish_downloaded(self, redis_key: str, url: str) -> None:
        await broker.publish(
            message={"storage_key": redis_key, "url": url},
            queue=DOWNLOADED_PAGES,
        )
        logger.info(
            " [✓] Задача в очередь `%s`: url=%s",
            DOWNLOADED_PAGES.name,
            url,
        )
