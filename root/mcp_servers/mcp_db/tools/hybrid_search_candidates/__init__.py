from root.persistence.relational_store import sessionmaker
from root.persistence.services.hybrid_search import HybridSearchService
from root.shared.observability import metrics

from .schemas import HybridSearchCandidatesInput

__all__ = ["hybrid_search_candidates_tool", "HybridSearchCandidatesInput"]


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
            async with sessionmaker() as session:
                items = await HybridSearchService.search(
                    session,
                    query=query,
                    city=city,
                    min_price=min_price,
                    max_price=max_price,
                    limit=limit,
                )
        except Exception:
            metrics.inc("mcp.db.hybrid_search_candidates.fail")
            raise
        metrics.inc("mcp.db.hybrid_search_candidates.success")
        return {"ok": True, "items": items, "count": len(items)}
