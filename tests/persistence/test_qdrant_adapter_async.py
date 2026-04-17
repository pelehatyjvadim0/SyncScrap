import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from root.persistence.vector_store.adapter import QdrantAdapter
from root.shared.config import settings


def test_qdrant_adapter_async_search_smoke() -> None:
    adapter = QdrantAdapter(vector_size=settings.qdrant.VECTOR_SIZE)
    point = SimpleNamespace(id="p1", score=0.91, payload={"idempotency_key": "k1"})
    adapter._client = SimpleNamespace(  # type: ignore[attr-defined]
        query_points=AsyncMock(return_value=SimpleNamespace(points=[point])),
    )

    async def _run() -> list[dict]:
        return await adapter.search(vector=[0.1] * settings.qdrant.VECTOR_SIZE, limit=5)

    out = asyncio.run(_run())
    assert len(out) == 1
    assert out[0]["id"] == "p1"
    assert out[0]["score"] == 0.91
    assert out[0]["payload"]["idempotency_key"] == "k1"


def test_qdrant_adapter_async_ensure_collection_creates_when_missing() -> None:
    adapter = QdrantAdapter(vector_size=settings.qdrant.VECTOR_SIZE)
    adapter._client = SimpleNamespace(  # type: ignore[attr-defined]
        get_collections=AsyncMock(return_value=SimpleNamespace(collections=[])),
        create_collection=AsyncMock(return_value=None),
    )

    async def _run() -> None:
        await adapter.ensure_collection()

    asyncio.run(_run())
    adapter._client.create_collection.assert_awaited_once()  # type: ignore[attr-defined]
