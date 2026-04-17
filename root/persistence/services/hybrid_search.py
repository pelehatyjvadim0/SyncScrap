import asyncio
from collections import defaultdict
from decimal import Decimal
from typing import Any, TYPE_CHECKING

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from root.shared.config import settings
from root.persistence.relational_store.models.listing_version import ListingVersion
from root.persistence.services.rerank import CrossEncoderReranker

if TYPE_CHECKING:
    from root.persistence.vector_store.adapter import QdrantAdapter
    from root.persistence.vector_store.encoder import VectorEncoder


class HybridSearchService:
    _qdrant: Any | None = None
    _encoder: Any | None = None
    _init_lock = asyncio.Lock()

    @classmethod
    async def initialize(cls) -> None:
        # Инициализация тяжелых зависимостей делается на старте сервера.
        if not settings.qdrant.ENABLED:
            return
        async with cls._init_lock:
            from root.persistence.vector_store.adapter import QdrantAdapter
            from root.persistence.vector_store.encoder import VectorEncoder

            if cls._encoder is None:
                loop = asyncio.get_running_loop()
                cls._encoder = await loop.run_in_executor(None, VectorEncoder)
            if cls._qdrant is None:
                encoder = cls._encoder
                if encoder is None:
                    raise RuntimeError("VectorEncoder не инициализирован")
                cls._qdrant = QdrantAdapter(vector_size=encoder.vector_size)
                await cls._qdrant.ensure_collection()

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

        vector_score_by_key: dict[str, float] = defaultdict(float)
        if settings.qdrant.ENABLED:
            if cls._encoder is None or cls._qdrant is None:
                await cls.initialize()
            if cls._encoder is None or cls._qdrant is None:
                raise RuntimeError("Не удалось инициализировать VectorEncoder или QdrantAdapter")

            loop = asyncio.get_running_loop()
            query_vector = await loop.run_in_executor(None, cls._encoder.encode, query)
            vector_hits = await cls._qdrant.search(vector=query_vector, limit=limit * 3)
            for hit in vector_hits:
                key = str(hit.get("payload", {}).get("idempotency_key") or "")
                if key:
                    vector_score_by_key[key] = max(
                        vector_score_by_key[key],
                        float(hit.get("score", 0.0)),
                    )

        ranked: list[dict[str, Any]] = []
        for row in sql_candidates:
            rerank = CrossEncoderReranker.score(
                query=query,
                title=row.title,
                price=float(row.price) if row.price is not None else None,
            )
            v_score = vector_score_by_key.get(row.idempotency_key, 0.0)
            total = rerank if not settings.qdrant.ENABLED else 0.6 * rerank + 0.4 * v_score
            ranked.append(
                {
                    "listing_id": row.idempotency_key,
                    "score": total,
                    "reason": "sql_rerank" if not settings.qdrant.ENABLED else "hybrid_sql_vector_rerank",
                    "title": row.title,
                    "price": float(row.price) if row.price is not None else None,
                    "city": row.city,
                    "url": row.attributes.get("url"),
                }
            )
        ranked.sort(key=lambda x: x["score"], reverse=True)
        return ranked[:limit]
