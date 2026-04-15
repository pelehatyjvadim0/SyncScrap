import json
import logging

import httpx

from root.shared.dead_letter import publish_dead_letter
from root.shared.queues import DISCOVERED_ITEMS, DISCOVERY_URLS
from root.shared.rabbitmq import broker, faststream_app
from root.contracts.v1.pipeline_messages import DeltaCandidate, DiscoveryTask
from root.apps.workers.scout.logic.scout_service import ScoutService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@broker.subscriber(DISCOVERY_URLS)
async def handle_discovery_task(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)
    task = DiscoveryTask.model_validate(payload)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        response = await client.get(str(task.search_url))
        response.raise_for_status()
        listings = ScoutService.parse_discovery_page(
            html=response.text,
            source=task.source,
            base_url=str(task.search_url),
            city=task.city,
        )

    if not listings:
        await publish_dead_letter(
            stage="scout",
            reason="empty_discovery_result",
            payload=payload,
        )
        return

    for listing in listings:
        await broker.publish(
            message=DeltaCandidate(listing=listing).model_dump(mode="json"),
            queue=DISCOVERED_ITEMS,
        )
    logger.info(" [Scout] published discovered_items=%s", len(listings))


@faststream_app.after_startup
async def _startup() -> None:
    logger.info(" [Scout] worker started")
