import json
import logging

from root.shared.dead_letter import publish_dead_letter
from root.shared.config import settings
from root.shared.downloader import Downloader
from root.shared.parsing_failures import resolve_failure_reason
from root.shared.queues import DISCOVERED_ITEMS, DISCOVERY_URLS
from root.shared.rabbitmq import broker, faststream_app
from root.shared.resources import res
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
    html: str | None = None
    try:
        task = DiscoveryTask.model_validate(payload)

        client = await res.get_http_client()
        html = await Downloader.fetch_html(
            client,
            str(task.search_url),
            max_retries=settings.downloader.MAX_RETRIES,
            base_delay_seconds=settings.downloader.BASE_DELAY_SECONDS,
        )
        listings = ScoutService.parse_discovery_page(
            html=html,
            source=task.source,
            base_url=str(task.search_url),
            city=task.city,
        )
    except Exception as exc:
        reason = resolve_failure_reason(
            fallback="scout_processing_failed",
            html=html,
            exc=exc,
        )
        await publish_dead_letter(
            stage="scout",
            reason=reason,
            payload=payload,
        )
        return

    if not listings:
        reason = resolve_failure_reason(
            fallback="empty_discovery_result",
            html=html,
        )
        await publish_dead_letter(
            stage="scout",
            reason=reason,
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
    await res.init_all()
    logger.info(" [Scout] worker started")


@faststream_app.on_shutdown
async def _shutdown() -> None:
    await res.close_all()
