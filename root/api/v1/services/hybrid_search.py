from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from root.api.v1.services.rerank import CrossEncoderReranker
from root.persistence.models.listing_version import ListingVersion
from root.shared.vector_store import QdrantAdapter, hash_embedding


class HybridSearchService:
    _qdrant = QdrantAdapter()

    @classmethod
    async def search(
        cls,
        session: AsyncSession,
        *,
        query: str,
        city: str | None,
        min_price: float | None,
        max_price: float | None,
        limit: int,
    ) -> list[dict[str, Any]]:
        filters = []
        if city:
            filters.append(ListingVersion.city == city)
        if min_price is not None:
            filters.append(ListingVersion.price >= Decimal(str(min_price)))
        if max_price is not None:
            filters.append(ListingVersion.price <= Decimal(str(max_price)))

        stmt = select(ListingVersion).order_by(desc(ListingVersion.created_at)).limit(200)
        if filters:
            stmt = stmt.where(and_(*filters))
        rows = (await session.execute(stmt)).scalars().all()
        latest_by_key: dict[str, ListingVersion] = {}
        for row in rows:
            if row.idempotency_key not in latest_by_key:
                latest_by_key[row.idempotency_key] = row
        sql_candidates = list(latest_by_key.values())

        query_vector = hash_embedding(query, 64)
        vector_hits = cls._qdrant.search(vector=query_vector, limit=limit * 3)
        vector_score_by_key: dict[str, float] = defaultdict(float)
        for hit in vector_hits:
            key = str(hit.get("payload", {}).get("idempotency_key") or "")
            if key:
                vector_score_by_key[key] = max(vector_score_by_key[key], float(hit.get("score", 0.0)))

        ranked: list[dict[str, Any]] = []
        for row in sql_candidates:
            rerank = CrossEncoderReranker.score(
                query=query,
                title=row.title,
                price=float(row.price) if row.price is not None else None,
            )
            v_score = vector_score_by_key.get(row.idempotency_key, 0.0)
            total = 0.6 * rerank + 0.4 * v_score
            ranked.append(
                {
                    "listing_id": row.idempotency_key,
                    "score": total,
                    "reason": "hybrid_sql_vector_rerank",
                    "title": row.title,
                    "price": float(row.price) if row.price is not None else None,
                    "city": row.city,
                    "url": row.attributes.get("url"),
                }
            )
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:limit]
