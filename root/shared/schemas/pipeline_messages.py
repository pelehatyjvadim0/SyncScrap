from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, HttpUrl

from root.shared.schemas.canonical_listing import CanonicalListing
from root.shared.schemas.discovered_listing import DiscoveredListing


class DiscoveryTask(BaseModel):
    source: str = Field(default="avito", min_length=2, max_length=32)
    search_url: HttpUrl
    city: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=128)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeltaCandidate(BaseModel):
    listing: DiscoveredListing


class ExtractionTask(BaseModel):
    listing: DiscoveredListing
    force_refresh: bool = False


class HunterResult(BaseModel):
    listing: DiscoveredListing
    storage_key: str
    downloaded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NormalizedItem(BaseModel):
    listing: CanonicalListing
    source_url: HttpUrl
    raw_features: dict[str, Any] = Field(default_factory=dict)


class EmbeddingTask(BaseModel):
    listing_id: str
    idempotency_key: str
    version: int
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class RetrievalQuery(BaseModel):
    query: str
    city: str | None = None
    min_price: Decimal | None = None
    max_price: Decimal | None = None
    limit: int = Field(default=10, ge=1, le=50)


class RetrievalResult(BaseModel):
    listing_id: str
    score: float
    reason: str
    payload: dict[str, Any]
