import hashlib
import logging
from collections.abc import Iterable
from typing import Any

from root.shared.config import settings

logger = logging.getLogger(__name__)


def hash_embedding(text: str, size: int) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [digest[i % len(digest)] / 255 for i in range(size)]
    return values


class QdrantAdapter:
    def __init__(self) -> None:
        self._enabled = False
        self._client = None
        self._init_client()

    def _init_client(self) -> None:
        try:
            from qdrant_client import QdrantClient  # type: ignore

            self._client = QdrantClient(
                url=settings.qdrant.URL,
                api_key=settings.qdrant.API_KEY,
            )
            self._enabled = True
        except Exception as exc:
            logger.warning(" [Qdrant] fallback local mode: %s", exc)
            self._enabled = False

    def upsert(self, *, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        if not self._enabled or self._client is None:
            return
        from qdrant_client.models import PointStruct  # type: ignore

        self._client.upsert(
            collection_name=settings.qdrant.COLLECTION_NAME,
            wait=False,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    def search(self, *, vector: list[float], limit: int) -> list[dict[str, Any]]:
        if not self._enabled or self._client is None:
            return []
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
        if not self._enabled or self._client is None:
            return
        from qdrant_client.models import Distance, VectorParams  # type: ignore

        collections = self._client.get_collections().collections
        names: Iterable[str] = [c.name for c in collections]
        if settings.qdrant.COLLECTION_NAME in names:
            return
        self._client.create_collection(
            collection_name=settings.qdrant.COLLECTION_NAME,
            vectors_config=VectorParams(
                size=settings.qdrant.VECTOR_SIZE,
                distance=Distance.COSINE,
            ),
        )
