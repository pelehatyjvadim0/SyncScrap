import logging

from root.shared.queues import RAW_URLS
from root.shared.rabbitmq import broker

logger = logging.getLogger(__name__)


class URLSpawner:
    @classmethod
    async def append_urls_in_queue(cls, list_urls: list[str]) -> None:
        logger.info("Start publishing URLs to queue")
        sent_counter = 0

        for url in list_urls:
            try:
                await broker.publish(message=url, queue=RAW_URLS)
                sent_counter += 1
            except Exception as exc:
                logger.error("Failed to publish URL %s: %s", url, exc)

        logger.info(
            "Publishing completed. Total=%s, sent=%s",
            len(list_urls),
            sent_counter,
        )
