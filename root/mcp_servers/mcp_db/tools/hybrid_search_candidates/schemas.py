from pydantic import BaseModel, Field


class HybridSearchCandidatesInput(BaseModel):
    query: str = Field(min_length=1)
    city: str | None = None
    min_price: float | None = Field(default=None, ge=0)
    max_price: float | None = Field(default=None, ge=0)
    limit: int = Field(default=10, ge=1, le=50)
