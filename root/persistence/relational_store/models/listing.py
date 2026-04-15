from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from root.persistence.models.base import BaseModel


class Listing(BaseModel):
    """Унифицированная строка выдачи парсера: любой домен, специфика - в `extra`."""

    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    title: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[Decimal] = mapped_column(
        Numeric(precision=10, scale=2), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, init=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, onupdate=func.now()
    )
    extra: Mapped[dict] = mapped_column(JSONB, default_factory=dict, nullable=True)
