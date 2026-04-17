import json
import logging

from root.persistence.relational_store.connection import sessionmaker
from root.persistence.relational_store.dao.ingestion_event import IngestionEventDAO
from root.persistence.relational_store.dao.listing_version import ListingVersionDAO
from root.persistence.relational_store.dao.listing_state import ListingStateDAO
from root.shared.config import settings
from root.shared.dead_letter import publish_dead_letter
from root.shared.queues import EMBEDDING_TASKS, NORMALIZED_ITEMS
from root.shared.rabbitmq import broker, faststream_app
from root.shared.resources import res
from root.contracts.v1.pipeline_messages import EmbeddingTask, HunterResult
from root.apps.workers.normalize.logic.normalize_service import NormalizeService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@broker.subscriber(NORMALIZED_ITEMS)
async def handle_normalize(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
    hunter_result = HunterResult.model_validate(payload)
    listing = hunter_result.listing

    storage = await res.get_storage()
    html = await storage.get_html(hunter_result.storage_key)
    if not html:
        await publish_dead_letter(
            stage="normalize",
            reason="missing_html_in_redis",
            payload=payload,
        )
        return

    async with sessionmaker() as session:
        state = await ListingStateDAO.get_by_idempotency_key(session, listing.idempotency_key)
        version = state.version if state else 1
        canonical = NormalizeService.to_canonical(listing=listing, html=html, version=version)

        await ListingVersionDAO.insert_version(
            session,
            {
                "idempotency_key": canonical.idempotency_key,
                "version": canonical.version,
                "title": canonical.title,
                "description_markdown": canonical.description_markdown,
                "price": canonical.price,
                "currency": canonical.currency,
                "city": canonical.city,
                "content_hash": canonical.content_hash,
                "attributes": canonical.attributes,
            },
        )
        await IngestionEventDAO.add(
            session,
            stage="normalize",
            idempotency_key=canonical.idempotency_key,
            payload={"version": canonical.version, "url": str(canonical.url)},
        )
        await session.commit()

    if settings.embedding.ENABLED and settings.qdrant.ENABLED:
        embedding_task = EmbeddingTask(
            listing_id=canonical.listing_id,
            idempotency_key=canonical.idempotency_key,
            version=canonical.version,
            text=f"{canonical.title}\n{canonical.description_markdown}",
            metadata={
                "price": float(canonical.price) if canonical.price is not None else None,
                "city": canonical.city,
                "scam_score": canonical.scam_score,
                "url": str(canonical.url),
            },
        )
        await broker.publish(message=embedding_task.model_dump(mode="json"), queue=EMBEDDING_TASKS)
        logger.info(" [Normalize] canonical saved and embedding queued: %s", canonical.idempotency_key)
    else:
        logger.info(" [Normalize] canonical saved without embedding: %s", canonical.idempotency_key)


@faststream_app.after_startup
async def _startup() -> None:
    logger.info(" [Normalize] worker started")
