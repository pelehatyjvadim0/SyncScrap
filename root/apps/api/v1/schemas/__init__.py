# Pydantic-схемы тела HTTP-запросов и ответов API - отдельно от contracts v1 (там сообщения брокера).

from root.apps.api.v1.schemas.bulk_targets import BulkTargetsRequest, BulkTargetsResponse
from root.apps.api.v1.schemas.discovery import (
    DiscoveryEnqueueRequest,
    DiscoveryEnqueueResponse,
)
from root.apps.api.v1.schemas.search import (
    HybridSearchItem,
    HybridSearchRequest,
    HybridSearchResponse,
)

__all__ = [
    "BulkTargetsRequest",
    "BulkTargetsResponse",
    "DiscoveryEnqueueRequest",
    "DiscoveryEnqueueResponse",
    "HybridSearchItem",
    "HybridSearchRequest",
    "HybridSearchResponse",
]
