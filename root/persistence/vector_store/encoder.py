from sentence_transformers import SentenceTransformer

from root.shared.config import settings


class VectorEncoder:
    def __init__(self) -> None:
        self._model = SentenceTransformer(settings.embedding.MODEL_NAME)
        self.vector_size = self._model.get_sentence_embedding_dimension()
        if settings.qdrant.VECTOR_SIZE != self.vector_size:
            raise ValueError(
                f"QDRANT_VECTOR_SIZE must be {self.vector_size} for "
                f"{settings.embedding.MODEL_NAME}, got {settings.qdrant.VECTOR_SIZE}"
            )

    def encode(self, text: str) -> list[float]:
        vector = self._model.encode(text, normalize_embeddings=True)
        return vector.tolist()
