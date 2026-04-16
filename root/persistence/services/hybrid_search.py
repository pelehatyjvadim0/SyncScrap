import asyncio
from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.relational_store.models.listing_version import ListingVersion
from root.persistence.services.rerank import CrossEncoderReranker
from root.persistence.vector_store import QdrantAdapter, VectorEncoder


class HybridSearchService:
    _qdrant = QdrantAdapter()
    _encoder = VectorEncoder()

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

        stmt = select(ListingVersion).order_by(desc(ListingVersion.created_at)).limit(200) # сортируем по убыванию даты создания версии, в latest_by_key будут только последние версии для каждого idempotency_key
        if filters:
            stmt = stmt.where(and_(*filters))
        rows = (await session.execute(stmt)).scalars().all()
        latest_by_key: dict[str, ListingVersion] = {} # словарь с последними версиями для каждого idempotency_key
        for row in rows:
            if row.idempotency_key not in latest_by_key: # добавляем только последнюю версию для каждого idempotency_key
                latest_by_key[row.idempotency_key] = row
        sql_candidates = list(latest_by_key.values())

        loop = asyncio.get_running_loop()
        query_vector = await loop.run_in_executor(None, cls._encoder.encode, query)
        vector_hits = await cls._qdrant.search(vector=query_vector, limit=limit * 3)
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
