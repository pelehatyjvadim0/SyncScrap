# Лёгкая карточка с этапа Scout - до глубокого скрапа; idempotency_key связывает пайплайн.
# Не добавлять сюда полный HTML - только то, что нужно для delta и маршрутизации.

from datetime import datetime, timezone
from decimal import Decimal
from hashlib import sha1
from typing import Any

from pydantic import BaseModel, Field, HttpUrl, field_validator


def _price_to_decimal(value: Any) -> Decimal:
    if isinstance(value, Decimal):
        return value
    if isinstance(value, (int, float, str)):
        return Decimal(str(value))
    raise TypeError(f"Unsupported price type: {type(value)!r}")


class DiscoveredListing(BaseModel):
    source: str = Field(default="avito", min_length=2, max_length=32)
    listing_id: str = Field(min_length=1, max_length=128)
    url: HttpUrl
    price: Decimal | None = None
    title_short: str | None = Field(default=None, max_length=512)
    city: str | None = Field(default=None, max_length=128)
    seen_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("price", mode="before")
    @classmethod
    def _validate_price(cls, value: Any) -> Decimal | None:
        if value is None:
            return None
        return _price_to_decimal(value)

    @property
    def idempotency_key(self) -> str:
        return f"{self.source}:{self.listing_id}"

    @property
    def content_hash_light(self) -> str:
        base = "|".join(
            [
                self.idempotency_key,
                str(self.price or ""),
                (self.title_short or "").strip().lower(),
                (self.city or "").strip().lower(),
            ]
        )
        return sha1(base.encode("utf-8")).hexdigest()
