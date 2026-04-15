from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from root.persistence.models.base import BaseModel


class ListingVersion(BaseModel):
    __tablename__ = "listing_versions"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    idempotency_key: Mapped[str] = mapped_column(String(256), index=True)
    version: Mapped[int] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description_markdown: Mapped[str] = mapped_column(Text, default="")
    price: Mapped[Decimal | None] = mapped_column(Numeric(precision=12, scale=2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="RUB")
    city: Mapped[str | None] = mapped_column(String(128), nullable=True)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    attributes: Mapped[dict] = mapped_column(JSONB, default_factory=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
