from datetime import datetime

from sqlalchemy import String, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from root.persistence.relational_store.models.base import BaseModel


class IngestionEvent(BaseModel):
    __tablename__ = "ingestion_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    stage: Mapped[str] = mapped_column(String(64), index=True)
    idempotency_key: Mapped[str | None] = mapped_column(String(256), nullable=True, index=True)
    
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
  
    created_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ok")
    payload: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
