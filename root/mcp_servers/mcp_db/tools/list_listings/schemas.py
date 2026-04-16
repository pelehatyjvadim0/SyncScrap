from pydantic import BaseModel, Field


class ListListingsInput(BaseModel):
    city: str | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
