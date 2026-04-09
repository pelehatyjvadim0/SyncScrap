from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Numeric, func, String
from sqlalchemy.dialects.postgresql import JSONB
from decimal import Decimal
from app.core.models import BaseModel
from datetime import datetime


class Books(BaseModel):
    __tablename__ = "books"
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
        server_default=func.now(), nullable=False, onupdate=func.now(), init=False
    )
    extra: Mapped[dict] = mapped_column(JSONB, default_factory=dict, nullable=True)
