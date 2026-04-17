import json
import logging

from root.persistence.connection import sessionmaker
from root.persistence.dao.ingestion_event import IngestionEventDAO
from root.persistence.dao.listing_state import ListingStateDAO
from root.shared.dead_letter import publish_dead_letter
from root.shared.queues import DISCOVERED_ITEMS, EXTRACTION_URLS
from root.shared.rabbitmq import broker, faststream_app
from root.contracts.v1.pipeline_messages import DeltaCandidate, ExtractionTask

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@broker.subscriber(DISCOVERED_ITEMS)
async def handle_delta(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
    candidate = DeltaCandidate.model_validate(payload)
    listing = candidate.listing

    async with sessionmaker() as session:
        state = await ListingStateDAO.get_by_idempotency_key(session, listing.idempotency_key)
        should_extract = state is None
        next_version = 1
        if state is not None:
            next_version = state.version + 1
            changed_price = state.last_seen_price != listing.price
            changed_hash = state.content_hash_light != listing.content_hash_light
            should_extract = changed_price or changed_hash

        await ListingStateDAO.touch_state(
            session,
            source=listing.source,
            listing_id=listing.listing_id,
            idempotency_key=listing.idempotency_key,
            url=str(listing.url),
            price=listing.price,
            content_hash_light=listing.content_hash_light,
            next_version=next_version,
        )
        await IngestionEventDAO.add(
            session,
            stage="delta_filter",
            status="changed" if should_extract else "no_change",
            idempotency_key=listing.idempotency_key,
            payload={"url": str(listing.url), "version": next_version},
        )
        await session.commit()

    if not should_extract:
        logger.info(" [Delta] skip unchanged %s", listing.idempotency_key)
        return

    try:
        await broker.publish(
            message=ExtractionTask(listing=listing, force_refresh=True).model_dump(mode="json"),
            queue=EXTRACTION_URLS,
        )
    except Exception as exc:
        await publish_dead_letter(
            stage="delta_filter",
            reason=f"publish_extraction_failed:{exc}",
            payload=payload,
        )
        raise

    logger.info(" [Delta] queued extraction %s", listing.idempotency_key)


@faststream_app.after_startup
async def _startup() -> None:
    logger.info(" [Delta] worker started")
