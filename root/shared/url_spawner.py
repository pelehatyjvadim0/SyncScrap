# Публикация задач discovery в очередь RabbitMQ (без legacy raw_urls/download).

import logging

from pydantic import HttpUrl

from root.shared.queues import DISCOVERY_URLS
from root.shared.rabbitmq import broker
from root.contracts.v1.pipeline_messages import DiscoveryTask

logger = logging.getLogger(__name__)


class URLSpawner:
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
