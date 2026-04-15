from pydantic import BaseModel, Field


class HybridSearchRequest(BaseModel):
    query: str = Field(min_length=2)
    city: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    limit: int = Field(default=10, ge=1, le=30)


class HybridSearchItem(BaseModel):
    listing_id: str
    score: float
    reason: str
    title: str
    price: float | None
    city: str | None
    url: str | None
    scam_score: float | None = None


class HybridSearchResponse(BaseModel):
    items: list[HybridSearchItem]
