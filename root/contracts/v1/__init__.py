# Реэкспорт контрактов v1 - импортируй отсюда или из подмодулей root.contracts.v1.*.
# Версия контрактов сообщений пайплайна (v1). Единая точка импорта для воркеров и API.
# Не смешивать с бизнес-логикой - только Pydantic-модели и общие поля пайплайна.

from root.contracts.v1.canonical_listing import CanonicalListing
from root.contracts.v1.discovered_listing import DiscoveredListing
from root.contracts.v1.listing import ListingRecord
from root.contracts.v1.pipeline_messages import (
    DeltaCandidate,
    DiscoveryTask,
    EmbeddingTask,
    ExtractionTask,
    HunterResult,
    NormalizedItem,
    RetrievalQuery,
    RetrievalResult,
)
from root.contracts.v1.raw_url_message import RawUrlMessage

__all__ = [
    "CanonicalListing",
    "DeltaCandidate",
    "DiscoveredListing",
    "DiscoveryTask",
    "EmbeddingTask",
    "ExtractionTask",
    "HunterResult",
    "ListingRecord",
    "NormalizedItem",
    "RawUrlMessage",
    "RetrievalQuery",
    "RetrievalResult",
]
