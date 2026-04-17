import json
import logging

from root.persistence.relational_store.connection import sessionmaker
from root.persistence.relational_store.dao.ingestion_event import IngestionEventDAO
from root.shared.queues import DEAD_LETTER
from root.shared.rabbitmq import broker, faststream_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@broker.subscriber(DEAD_LETTER)
async def handle_dead_letter(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
    stage = payload.get("stage", "unknown")
    reason = payload.get("reason", "unknown")

    async with sessionmaker() as session:
        await IngestionEventDAO.add(
            session,
            stage=f"dlq.{stage}",
            status="error",
            message=reason,
            payload=payload,
        )
        await session.commit()
    logger.error(" [DLQ] stage=%s reason=%s", stage, reason)


@faststream_app.after_startup
async def _startup() -> None:
    logger.info(" [Observability] DLQ watcher started")
