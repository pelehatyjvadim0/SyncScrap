from pydantic import BaseModel, Field, HttpUrl


class OrchestratorIntentRequest(BaseModel):
    source: str = "avito"
    city: str | None = None
    category: str | None = None
    search_urls: list[HttpUrl] = Field(default_factory=list)


class OrchestratorIntentResponse(BaseModel):
    tool: str
    result: dict
