import asyncio
import logging

from pydantic import HttpUrl

from root.shared.queues import DISCOVERY_URLS, RAW_URLS, RAW_URLS_PLAYWRIGHT
from root.shared.rabbitmq import broker
from root.shared.schemas.pipeline_messages import DiscoveryTask
from root.shared.schemas.raw_url_message import RawUrlMessage

logger = logging.getLogger(__name__)


class URLSpawner:
    @classmethod
    async def append_urls_in_queue(
        cls,
        list_urls: list[str],
        *, # аргументы до звёздочки - позиционные, после звёздочки - все именованные, тут это контракт на именованные аргументы!!!!!!
        force_refresh: bool = False,
        publish_gap_seconds: float = 0.0,
    ) -> list[str]:
        """
        Публикует URL в raw_urls. Возвращает список успешно отправленных (для планировщика / метрик).
        """
        logger.info(
            " [↑] Публикация в raw_urls: всего=%s force_refresh=%s пауза=%ss",
            len(list_urls),
            force_refresh,
            publish_gap_seconds,
        )
        sent: list[str] = []

        for i, url in enumerate(list_urls):
            try:
                payload = RawUrlMessage(url=HttpUrl(url), force_refresh=force_refresh)
                await broker.publish(message=payload.model_dump_json(), queue=RAW_URLS) # в json дампим чтобы из httpurl перевести в строку
                sent.append(url)
                logger.debug(" [↑] Отправлено в raw_urls (%s/%s): %s", i + 1, len(list_urls), url)
            except Exception as exc:
                logger.error(" [↑] Не удалось опубликовать URL %s: %s", url, exc)

            if publish_gap_seconds > 0 and i + 1 < len(list_urls):
                await asyncio.sleep(publish_gap_seconds)

        logger.info(
            " [↑] Публикация завершена: успешно=%s из %s",
            len(sent),
            len(list_urls),
        )
        return sent

    @classmethod
    async def append_discovery_tasks(
        cls,
        list_urls: list[str],
        *,
        source: str = "avito",
        city: str | None = None,
        category: str | None = None,
    ) -> list[str]:
        sent: list[str] = []
        for url in list_urls:
            try:
                task = DiscoveryTask(
                    source=source,
                    search_url=HttpUrl(url),
                    city=city,
                    category=category,
                )
                await broker.publish(
                    message=task.model_dump(mode="json"),
                    queue=DISCOVERY_URLS,
                )
                sent.append(url)
            except Exception as exc:
                logger.error(" [↑] Не удалось опубликовать discovery URL %s: %s", url, exc)
        logger.info(" [↑] discovery_urls: успешно=%s из %s", len(sent), len(list_urls))
        return sent

    @classmethod
    async def append_urls_in_playwright_queue(
        cls,
        list_urls: list[str],
        *,
        force_refresh: bool = False,
        publish_gap_seconds: float = 0.0,
    ) -> list[str]:
        # Публикует URL в raw_urls_playwright (Chromium, сценарии в worker_playwright).
        logger.info(
            " [↑] Публикация в raw_urls_playwright: всего=%s force_refresh=%s пауза=%ss",
            len(list_urls),
            force_refresh,
            publish_gap_seconds,
        )
        sent: list[str] = []

        for i, url in enumerate(list_urls):
            try:
                payload = RawUrlMessage(url=HttpUrl(url), force_refresh=force_refresh)
                await broker.publish(
                    message=payload.model_dump_json(),
                    queue=RAW_URLS_PLAYWRIGHT,
                )
                sent.append(url)
                logger.debug(
                    " [↑] Отправлено в raw_urls_playwright (%s/%s): %s",
                    i + 1,
                    len(list_urls),
                    url,
                )
            except Exception as exc:
                logger.error(" [↑] Не удалось опубликовать URL %s: %s", url, exc)

            if publish_gap_seconds > 0 and i + 1 < len(list_urls):
                await asyncio.sleep(publish_gap_seconds)

        logger.info(
            " [↑] raw_urls_playwright: успешно=%s из %s",
            len(sent),
            len(list_urls),
        )
        return sent
