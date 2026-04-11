import asyncio
import logging

from pydantic import HttpUrl

from root.shared.queues import RAW_URLS
from root.shared.rabbitmq import broker
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
