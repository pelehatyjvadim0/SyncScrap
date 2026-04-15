import logging
from typing import Any

from root.shared.queues import DEAD_LETTER
from root.shared.rabbitmq import broker

logger = logging.getLogger(__name__)


async def publish_dead_letter(
    *,
    stage: str,
    reason: str,
    payload: dict[str, Any],
) -> None:
    message = {"stage": stage, "reason": reason, "payload": payload}
    await broker.publish(message=message, queue=DEAD_LETTER)
    logger.warning(" [DLQ] %s reason=%s", stage, reason)
