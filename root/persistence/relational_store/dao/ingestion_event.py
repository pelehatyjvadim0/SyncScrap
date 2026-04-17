from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.relational_store.models.ingestion_event import IngestionEvent


class IngestionEventDAO:
    @staticmethod
    async def add(
        session: AsyncSession,
        *,
        stage: str,
        status: str = "ok",
        idempotency_key: str | None = None,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> None:
        stmt = insert(IngestionEvent).values(
            stage=stage,
            status=status,
            idempotency_key=idempotency_key,
            message=message,
            payload=payload or {},
        )
        await session.execute(stmt)
