import logging

from root.shared.queues import RAW_URLS
from root.shared.rabbitmq import broker
from root.shared.schemas import RawUrlMessage
from pydantic import HttpUrl
logger = logging.getLogger(__name__)


class URLSpawner:
    @classmethod
    async def append_urls_in_queue(cls, list_urls: list[str], force_refresh: bool = False) -> None:
        logger.info("Start publishing URLs to queue")
        sent_counter = 0

        for url in list_urls:
            try:
                payload = RawUrlMessage(url=HttpUrl(url), force_refresh=force_refresh)
                await broker.publish(message=payload.model_dump_json(), queue=RAW_URLS)
                sent_counter += 1
            except Exception as exc:
                logger.error("Failed to publish URL %s: %s", url, exc)

        logger.info(
            "Publishing completed. Total=%s, sent=%s",
            len(list_urls),
            sent_counter,
        )
