# Каноническое объявление после normalize - для Postgres listing_versions и эмбеддингов.
# Версия схемы - contracts v1; поля не раздувать без миграции и bump версии контракта.

from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha1
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


class CanonicalListing(BaseModel):
    source: str = Field(default="avito", min_length=2, max_length=32)
    listing_id: str = Field(min_length=1, max_length=128)
    idempotency_key: str = Field(min_length=3, max_length=256)
    version: int = Field(default=1, ge=1)
    url: HttpUrl
    title: str = Field(min_length=1, max_length=512)
    description_markdown: str = ""
    price: Decimal | None = None
    currency: str = Field(default="RUB", min_length=3, max_length=3)
    city: str | None = Field(default=None, max_length=128)
    attributes: dict[str, Any] = Field(default_factory=dict)
    scam_score: float = Field(default=0.0, ge=0, le=1)
    collected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("price", mode="before")
    @classmethod
    def _validate_price(cls, value: Any) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, Decimal):
            return value
        if isinstance(value, (int, float, str)):
            return Decimal(str(value))
        raise TypeError(f"Unsupported price type: {type(value)!r}")

    @property
    def content_hash(self) -> str:
        base = "|".join(
            [
                self.idempotency_key,
                self.title.strip().lower(),
                str(self.price or ""),
                (self.city or "").strip().lower(),
                self.description_markdown.strip().lower(),
            ]
        )
        return sha1(base.encode("utf-8")).hexdigest()
