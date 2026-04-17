from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from root.apps.api.v1.schemas import (
    BulkTargetsRequest,
    BulkTargetsResponse,
    HybridSearchItem,
    HybridSearchRequest,
    HybridSearchResponse,
    OrchestratorIntentRequest,
    OrchestratorIntentResponse,
)
from root.apps.api.v1.services import BulkTargetsService, InvalidTargetUrlError, OrchestratorService
from root.shared.dependencies import DependsGenerator
from root.shared.observability import metrics
from root.contracts.v1.pipeline_messages import RetrievalQuery
from root.apps.orchestrator.service import LLMOrchestrator, UserIntent

router = APIRouter()
orchestrator = LLMOrchestrator()


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
        min_price=body.min_price,
        max_price=body.max_price,
        limit=body.limit,
    )
    with metrics.timer("api.search.hybrid.ms"):
        items = await OrchestratorService.run_query(session, query)
    metrics.inc("api.search.hybrid.ok")
    return HybridSearchResponse(items=[HybridSearchItem.model_validate(item) for item in items])


@router.get("/health", summary="Простой healthcheck API")
async def healthcheck() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/metrics", summary="Базовые in-memory метрики")
async def read_metrics() -> dict:
    return metrics.snapshot()


@router.post(
    "/orchestrator/intent",
    response_model=OrchestratorIntentResponse,
    summary="LLM-orchestrator: запуск discovery по user intent",
)
async def orchestrator_intent(body: OrchestratorIntentRequest) -> OrchestratorIntentResponse:
    with metrics.timer("api.orchestrator.intent.ms"):
        result = await orchestrator.dispatch(
            UserIntent(
                source=body.source,
                city=body.city,
                category=body.category,
                search_urls=[str(url) for url in body.search_urls],
            )
        )
    metrics.inc("api.orchestrator.intent.ok")
    return OrchestratorIntentResponse.model_validate(result)
