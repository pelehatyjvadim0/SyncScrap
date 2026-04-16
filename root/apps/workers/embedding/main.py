import json
import logging

from root.persistence.connection import sessionmaker
from root.persistence.dao.ingestion_event import IngestionEventDAO
from root.shared.dead_letter import publish_dead_letter
from root.shared.queues import EMBEDDING_TASKS
from root.shared.rabbitmq import broker, faststream_app
from root.contracts.v1.pipeline_messages import EmbeddingTask
from root.persistence.vector_store import QdrantAdapter, VectorEncoder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

_qdrant = QdrantAdapter()
_encoder = VectorEncoder()


@faststream_app.after_startup
async def _startup() -> None:
    await _qdrant.ensure_collection()
    logger.info(" [Embedding] worker started")


@broker.subscriber(EMBEDDING_TASKS)
async def handle_embedding(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
    task = EmbeddingTask.model_validate(payload)

    try:
        vector = _encoder.encode(task.text)
        point_id = f"{task.idempotency_key}:v{task.version}"
        await _qdrant.upsert(
            point_id=point_id,
            vector=vector,
            payload={"listing_id": task.listing_id, "idempotency_key": task.idempotency_key, **task.metadata},
        )

        async with sessionmaker() as session:
            await IngestionEventDAO.add(
                session,
                stage="embedding",
                idempotency_key=task.idempotency_key,
                payload={"point_id": point_id},
            )
            await session.commit()
    except Exception as exc:
        await publish_dead_letter(
            stage="embedding",
            reason=f"embedding_failed:{exc}",
            payload=payload,
        )
        raise

    logger.info(" [Embedding] indexed %s", task.idempotency_key)
