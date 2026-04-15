from collections.abc import Iterable
from typing import Any, TypedDict

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

from root.shared.config import settings

class VectorSearchHit(TypedDict):
    id: str | int
    score: float
    payload: dict[str, Any]


class QdrantAdapter:
    def __init__(self, vector_size: int | None = None) -> None:
        self._client = QdrantClient(
            url=settings.qdrant.URL,
            api_key=settings.qdrant.API_KEY,
        )
        self._vector_size = vector_size or settings.qdrant.VECTOR_SIZE

    def upsert(
        self,
        *,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
        wait: bool = True,
    ) -> None:
        self._client.upsert(
            collection_name=settings.qdrant.COLLECTION_NAME,
            wait=wait,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    def search(self, *, vector: list[float], limit: int) -> list[VectorSearchHit]:
        points = self._client.search(
            collection_name=settings.qdrant.COLLECTION_NAME,
            query_vector=vector,
            limit=limit,
        )
        return [
            {
                "id": p.id,
                "score": float(p.score),
                "payload": dict(p.payload or {}),
            }
            for p in points
        ]

    def ensure_collection(self) -> None:
        if settings.qdrant.VECTOR_SIZE != self._vector_size:
            raise ValueError(
                f"QDRANT_VECTOR_SIZE must be {self._vector_size}, got {settings.qdrant.VECTOR_SIZE}"
            )
        collections = self._client.get_collections().collections
        names: Iterable[str] = [c.name for c in collections]
        if settings.qdrant.COLLECTION_NAME in names:
            return
        self._client.create_collection(
            collection_name=settings.qdrant.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )
