import asyncio
import logging

from root.persistence.relational_store.connection import sessionmaker
from root.persistence.services.hybrid_search import HybridSearchService
from root.shared.observability import metrics

from .schemas import HybridSearchCandidatesInput

__all__ = ["hybrid_search_candidates_tool", "HybridSearchCandidatesInput"]

logger = logging.getLogger(__name__)
POSTGRES_TIMEOUT_SECONDS = 5.0
QDRANT_TIMEOUT_SECONDS = 5.0
TOTAL_SEARCH_TIMEOUT_SECONDS = POSTGRES_TIMEOUT_SECONDS + QDRANT_TIMEOUT_SECONDS + 2.0


async def hybrid_search_candidates_tool(
    *,
    query: str,
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 10,
) -> dict:
    with metrics.timer("mcp.db.hybrid_search_candidates.latency_ms"):
        metrics.inc("mcp.db.hybrid_search_candidates.calls")
        try:
            async with asyncio.timeout(TOTAL_SEARCH_TIMEOUT_SECONDS):
                async with sessionmaker() as session:
                    items = await HybridSearchService.search(
                        session,
                        query=query,
                        city=city,
                        min_price=min_price,
                        max_price=max_price,
                        limit=limit,
                    )
        except TimeoutError as exc:
            logger.exception(" - mcp_db hybrid_search_candidates - превышен таймаут выполнения")
            metrics.inc("mcp.db.hybrid_search_candidates.timeout")
            raise RuntimeError("Превышен таймаут при обращении к Postgres/Qdrant") from exc
        except Exception:
            logger.exception(" - mcp_db hybrid_search_candidates - ошибка выполнения")
            metrics.inc("mcp.db.hybrid_search_candidates.fail")
            raise
        metrics.inc("mcp.db.hybrid_search_candidates.success")
        return {"ok": True, "items": items, "count": len(items)}
