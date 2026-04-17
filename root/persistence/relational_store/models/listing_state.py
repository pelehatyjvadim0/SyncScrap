from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from root.persistence.relational_store.models.base import BaseModel


class ListingState(BaseModel):
    __tablename__ = "listing_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    idempotency_key: Mapped[str] = mapped_column(String(256), unique=True, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False)
    listing_id: Mapped[str] = mapped_column(String(128), nullable=False)
    url: Mapped[str] = mapped_column(nullable=False)
    last_seen_price: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=12, scale=2), nullable=True
    )
    content_hash_light: Mapped[str | None] = mapped_column(String(64), nullable=True)
   
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, onupdate=func.now()
    )
    last_seen_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
