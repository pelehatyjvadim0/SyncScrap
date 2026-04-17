from pydantic import BaseModel, Field, HttpUrl


class DiscoveryEnqueueRequest(BaseModel):
    source: str = "avito"
    city: str | None = None
    category: str | None = None
    search_urls: list[HttpUrl] = Field(default_factory=list)


class DiscoveryEnqueueResponse(BaseModel):
    queued: list[str] = Field(default_factory=list)
    queued_count: int = 0
