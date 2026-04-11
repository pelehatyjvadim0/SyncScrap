from sqlalchemy.orm import Mapped, mapped_column
from root.persistence.models.base import BaseModel
from datetime import datetime
from sqlalchemy import func

class TargetUrl(BaseModel):
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    url: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    last_scraped_at: Mapped[datetime] = mapped_column(server_default=func.now(), nullable=False, init=False)