from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from root.apps.api.v1.schemas import (
    BulkTargetsRequest,
    BulkTargetsResponse,
    DiscoveryEnqueueRequest,
    DiscoveryEnqueueResponse,
    HybridSearchItem,
    HybridSearchRequest,
    HybridSearchResponse,
)
from root.apps.api.v1.services import (
    BulkTargetsService,
    DiscoveryService,
    InvalidTargetUrlError,
    SearchService,
)
from root.shared.dependencies import DependsGenerator
from root.shared.observability import metrics
from root.contracts.v1.pipeline_messages import RetrievalQuery

router = APIRouter()


@router.post(
    "/targets/bulk",
    response_model=BulkTargetsResponse,
    summary="Массовое добавление целей (скрап)",
)
async def add_targets_urls(
    body: BulkTargetsRequest,
    session: AsyncSession = Depends(DependsGenerator.get_db),
) -> BulkTargetsResponse:

    try:
        with metrics.timer("api.targets.bulk.ms"):
            result = await BulkTargetsService.add_urls(session, body.urls)
        metrics.inc("api.targets.bulk.ok")
        return result
    except InvalidTargetUrlError as exc:
        metrics.inc("api.targets.bulk.bad_request")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc


@router.post(
    "/search/hybrid",
    response_model=HybridSearchResponse,
    summary="Hybrid-поиск (SQL + Vector + Rerank + Guardrail)",
)
async def hybrid_search(
    body: HybridSearchRequest,
    session: AsyncSession = Depends(DependsGenerator.get_db),
) -> HybridSearchResponse:
    query = RetrievalQuery(
        query=body.query,
        city=body.city,
        min_price=Decimal(str(body.min_price)) if body.min_price is not None else None,
        max_price=Decimal(str(body.max_price)) if body.max_price is not None else None,
        limit=body.limit,
    )
    with metrics.timer("api.search.hybrid.ms"):
        items = await SearchService.run_query(session, query)
    metrics.inc("api.search.hybrid.ok")
    return HybridSearchResponse(items=[HybridSearchItem.model_validate(item) for item in items])


@router.get("/health", summary="Простой healthcheck API")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics", summary="Базовые in-memory метрики")
async def read_metrics() -> dict:
    return metrics.snapshot()


@router.post(
    "/discovery/enqueue",
    response_model=DiscoveryEnqueueResponse,
    summary="Поставить discovery URL в очередь",
)
async def enqueue_discovery(body: DiscoveryEnqueueRequest) -> DiscoveryEnqueueResponse:
    with metrics.timer("api.discovery.enqueue.ms"):
        queued = await DiscoveryService.enqueue(
            search_urls=[str(url) for url in body.search_urls],
            source=body.source,
            city=body.city,
            category=body.category,
        )
    metrics.inc("api.discovery.enqueue.ok")
    return DiscoveryEnqueueResponse(
        queued=queued,
        queued_count=len(queued),
    )
