from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from root.persistence.relational_store.models.base import BaseModel


class TargetUrl(BaseModel):
    __tablename__ = "target_urls"

    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(nullable=False, unique=True)
    last_scraped_at: Mapped[datetime | None] = mapped_column(nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False
    )
