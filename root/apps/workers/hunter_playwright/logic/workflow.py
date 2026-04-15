import logging

from root.shared.config import settings
from root.shared.rabbitmq import broker
from root.shared.queues import NORMALIZED_ITEMS
from root.shared.redis_client import RedisManager
from root.shared.url_hash import url_hash
from root.contracts.v1.pipeline_messages import ExtractionTask, HunterResult
from root.contracts.v1.raw_url_message import RawUrlMessage
from root.apps.workers.hunter_playwright.logic.browser.lifecycle import BrowserLifecycle
from root.apps.workers.hunter_playwright.logic.scenarios.registry import scenario_for_url

logger = logging.getLogger(__name__)


def _use_redis_cache(message: RawUrlMessage, cached_html: str | None) -> bool:
    if message.force_refresh:
        logger.debug(" [hunter] force_refresh=true - кеш Redis игнорируется")
        return False
    if cached_html is None:
        return False
    return True


class PlaywrightWorkflow:
    """Hunter: ExtractionTask -> HTML в Redis -> HunterResult в normalized_items."""

    def __init__(self, browser: BrowserLifecycle, storage: RedisManager) -> None:
        self._browser = browser
        self._storage = storage

    async def run_extraction_task(self, task: ExtractionTask) -> None:
        url = str(task.listing.url)
        redis_key = await url_hash(url)
        cached_html = await self._storage.get_html(redis_key)

        raw_message = RawUrlMessage(url=task.listing.url, force_refresh=task.force_refresh)
        if _use_redis_cache(raw_message, cached_html):
            logger.info(" [hunter] HTML из Redis (extraction_task). url=%s", url)
        else:
            await self._render_and_store(url, redis_key)

        hunter_result = HunterResult(listing=task.listing, storage_key=redis_key)
        await broker.publish(
            message=hunter_result.model_dump(mode="json"),
            queue=NORMALIZED_ITEMS,
        )
        logger.info(" [hunter] HunterResult -> normalized_items. key=%s", redis_key)

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
            logger.exception(" [hunter] Не удалось сохранить HTML в Redis. ключ=%s", redis_key)
            raise
        logger.info(" [hunter] HTML в Redis. url=%s ключ=%s", url, redis_key)
