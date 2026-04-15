import asyncio
import logging

from root.contracts.v1.pipeline_messages import DiscoveryTask
from root.shared.queues import DISCOVERY_URLS
from root.shared.rabbitmq import broker

logger = logging.getLogger(__name__)

# Ошибка публикации в RabbitMQ - оборачиваем низкоуровневые исключения.
class PublishError(RuntimeError):
    pass

# Публикуем DiscoveryTask в очередь с таймаутом - fail fast при проблемах брокера.
async def publish_discovery_task(
    *,
    task: DiscoveryTask,
    timeout_seconds: float,
) -> None:
    try:
        await asyncio.wait_for(
            broker.publish(message=task.model_dump(mode="json"), queue=DISCOVERY_URLS),
            timeout=timeout_seconds,
        )
        logger.info("DiscoveryTask опубликован в очередь %s", DISCOVERY_URLS.name)
    except Exception as exc:
        logger.error("Ошибка публикации DiscoveryTask в очередь %s: %s", DISCOVERY_URLS.name, exc)
        raise PublishError(str(exc)) from exc
