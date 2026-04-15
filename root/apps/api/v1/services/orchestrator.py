from root.apps.api.v1.services.guardrail import LocalGuardrail
from root.apps.api.v1.services.hybrid_search import HybridSearchService
from root.contracts.v1.pipeline_messages import RetrievalQuery
from sqlalchemy.ext.asyncio import AsyncSession


class OrchestratorService:
    @staticmethod
    async def run_query(session: AsyncSession, query: RetrievalQuery) -> list[dict]:
        candidates = await HybridSearchService.search(
            session,
            query=query.query,
            city=query.city,
            min_price=float(query.min_price) if query.min_price is not None else None,
            max_price=float(query.max_price) if query.max_price is not None else None,
            limit=query.limit,
        )
        filtered: list[dict] = []
        for item in candidates:
            ok, scam_score = LocalGuardrail.evaluate(item)
            item["scam_score"] = scam_score
            if ok:
                filtered.append(item)
        return filtered
