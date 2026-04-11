import logging
from typing import Any

from httpx import AsyncClient

from root.shared.config import settings
from root.shared.rabbitmq import broker
from root.shared.queues import DOWNLOADED_PAGES
from root.shared.redis_client import RedisManager
from root.shared.schemas import RawUrlMessage
from root.worker_downloader.logic.downloader import DownloaderLogic
from root.worker_downloader.logic.message_payload import (
    RawUrlPayloadError,
    decode_raw_bytes,
    parse_raw_url_message,
)
from root.worker_downloader.logic.utils import DownloaderUtils

logger = logging.getLogger(__name__)


def _use_redis_cache(message: RawUrlMessage, cached_html: str | None) -> bool:
    if message.force_refresh:
        logger.debug(" [↓] force_refresh=true — кеш Redis игнорируется")
        return False
    if cached_html is None:
        return False
    return True


class DownloadWorkflow:
    """Один проход: распарсить сообщение → HTML в Redis → очередь downloaded_pages."""

    def __init__(self, http_client: AsyncClient, storage: RedisManager) -> None:
        self._http = http_client
        self._storage = storage

    async def run(self, msg: Any) -> None:
        url: str | None = None
        raw = decode_raw_bytes(msg)
        logger.debug(" [↓] Сырое тело RAW_URLS (первые 200 симв.): %.200s", raw)

        try:
            message = parse_raw_url_message(raw)
        except RawUrlPayloadError as exc:
            logger.warning(" [↓] Отклонено сообщение RAW_URLS: %s", exc)
            raise
        url = str(message.url)
        logger.info(" [→] URL получен: %s force_refresh=%s", url, message.force_refresh)

        redis_key = await DownloaderUtils.get_url_hash(url)
        cached_html = await self._storage.get_html(redis_key)

        if _use_redis_cache(message, cached_html):
            logger.info(" [↻] HTML из Redis, загрузка по сети не нужна. url=%s", url)
        else:
            await self._download_and_store(url, redis_key)

        await self._publish_downloaded(redis_key, url)

    async def _download_and_store(self, url: str, redis_key: str) -> None:
        html = await DownloaderLogic.download_url(
            http_client=self._http,
            url=url,
            max_retries=settings.downloader.MAX_RETRIES,
            base_delay_seconds=settings.downloader.BASE_DELAY_SECONDS,
        )
        await DownloaderLogic.publish_in_storage(
            self._storage,
            redis_key,
            html,
            expire=settings.downloader.HTML_EXPIRE_SECONDS,
        )
        logger.info(" [✓] HTML сохранён в Redis. url=%s ключ=%s", url, redis_key)

    async def _publish_downloaded(self, redis_key: str, url: str) -> None:
        await broker.publish({"storage_key": redis_key, "url": url}, DOWNLOADED_PAGES)
        logger.info(
            " [✓] Задача в очередь `%s`: url=%s",
            DOWNLOADED_PAGES.name,
            url,
        )
