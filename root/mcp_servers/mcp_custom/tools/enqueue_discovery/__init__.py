from uuid import uuid4

from pydantic import ValidationError

from root.contracts.v1.pipeline_messages import DiscoveryTask
from root.mcp_servers.mcp_custom.payloads import build_error_payload
from root.shared.observability import metrics
from root.shared.queues import DISCOVERY_URLS
from root.shared.redis_client import redis_manager
from root.shared.shared_utils import generate_task_id

from .logic import rate_limiter
from .publisher import PublishError, publish_discovery_task
from .schemas import (
    IDEMPOTENCY_TTL_SECONDS,
    PUBLISH_TIMEOUT_SECONDS,
    RATE_LIMIT_MAX_CALLS,
    RATE_LIMIT_WINDOW_SECONDS,
    EnqueueDiscoveryInput,
    ErrorResponse,
    SuccessResponse,
)


# Публичный MCP-инструмент - валидирует вход, ограничивает частоту, дедуплицирует и публикует задачу.
async def enqueue_discovery_tool(
    *,
    search_url: str,
    source: str = "avito",
    city: str | None = None,
    category: str | None = None,
    trace_id: str | None = None,
    idempotency_key: str | None = None,
) -> ErrorResponse | SuccessResponse:
    payload = {k: v for k, v in locals().items() if v is not None}
    trace = trace_id or str(uuid4())
    idem = idempotency_key or generate_task_id(
        prefix="enqueue_discovery",
        data={
            "search_url": search_url,
            "source": source,
            "city": city,
            "category": category,
        },
    )

    with metrics.timer("mcp.custom.enqueue_discovery.latency_ms"):
        if not rate_limiter.allow():
            metrics.inc("mcp.custom.enqueue_discovery.rate_limited")
            return build_error_payload(
                error_code="rate_limited",
                message="Превышен лимит запросов для enqueue_discovery_tool",
                details={
                    "window_seconds": RATE_LIMIT_WINDOW_SECONDS,
                    "max_calls": RATE_LIMIT_MAX_CALLS,
                },
                trace_id=trace,
                idempotency_key=idem,
                retryable=True,
            )

        try:
            validated_input = EnqueueDiscoveryInput.model_validate(payload)
        except ValidationError as exc:
            metrics.inc("mcp.custom.enqueue_discovery.validation_error")
            return build_error_payload(
                error_code="validation_error",
                message="Некорректные входные данные enqueue_discovery",
                details=exc.errors(),
                trace_id=trace,
                idempotency_key=idem,
                retryable=False,
            )

        try:
            task = DiscoveryTask.model_validate(validated_input.model_dump(exclude={"trace_id", "idempotency_key"}))
        except ValidationError as exc:
            metrics.inc("mcp.custom.enqueue_discovery.validation_error")
            return build_error_payload(
                error_code="validation_error",
                message="Ошибка валидации DiscoveryTask",
                details=exc.errors(),
                trace_id=trace,
                idempotency_key=idem,
                retryable=False,
            )

        is_new = await redis_manager.set_nx_ttl(idem, IDEMPOTENCY_TTL_SECONDS)
        if not bool(is_new):
            metrics.inc("mcp.custom.enqueue_discovery.duplicate")
            return {
                "ok": True,
                "status": "duplicate_ignored",
                "queue_name": DISCOVERY_URLS.name,
                "trace_id": trace,
                "idempotency_key": idem,
                "task": task.model_dump(mode="json"),
            }

        try:
            await publish_discovery_task(task=task, timeout_seconds=PUBLISH_TIMEOUT_SECONDS)
        except PublishError as exc:
            metrics.inc("mcp.custom.enqueue_discovery.fail")
            return build_error_payload(
                error_code="broker_publish_failed",
                message="Не удалось опубликовать DiscoveryTask в брокер",
                details=str(exc),
                trace_id=trace,
                idempotency_key=idem,
                retryable=True,
            )

        metrics.inc("mcp.custom.enqueue_discovery.success")
        return {
            "ok": True,
            "status": "queued",
            "queue_name": DISCOVERY_URLS.name,
            "trace_id": trace,
            "idempotency_key": idem,
            "task": task.model_dump(mode="json"),
        }


__all__ = ["enqueue_discovery_tool", "IDEMPOTENCY_TTL_SECONDS"]
