from root.persistence.vector_store.adapter import QdrantAdapter
from root.persistence.vector_store.encoder import VectorEncoder

encoder = VectorEncoder()
adapter = QdrantAdapter(vector_size=encoder.vector_size)

__all__ = ["adapter", "encoder"]
