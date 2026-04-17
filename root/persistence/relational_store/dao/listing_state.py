from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.relational_store.models.listing_state import ListingState


class ListingStateDAO:
    @staticmethod
    async def get_by_idempotency_key(
        session: AsyncSession, idempotency_key: str
    ) -> ListingState | None:
        stmt = select(ListingState).where(ListingState.idempotency_key == idempotency_key)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def touch_state(
        session: AsyncSession,
        *,
        source: str,
        listing_id: str,
        idempotency_key: str,
        url: str,
        price: Decimal | None,
        content_hash_light: str | None,
        next_version: int,
    ) -> None:
        stmt = insert(ListingState).values(
            source=source,
            listing_id=listing_id,
            idempotency_key=idempotency_key,
            url=url,
            last_seen_price=price,
            content_hash_light=content_hash_light,
            version=next_version,
            last_seen_at=datetime.now(timezone.utc).replace(tzinfo=None),
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["idempotency_key"],
            set_={
                "url": stmt.excluded.url,
                "last_seen_price": stmt.excluded.last_seen_price,
                "content_hash_light": stmt.excluded.content_hash_light,
                "version": stmt.excluded.version,
                "last_seen_at": stmt.excluded.last_seen_at,
            },
        )
        await session.execute(stmt)

    @staticmethod
    async def mark_seen(session: AsyncSession, idempotency_key: str) -> None:
        stmt = (
            update(ListingState)
            .where(ListingState.idempotency_key == idempotency_key)
            .values(last_seen_at=datetime.now(timezone.utc).replace(tzinfo=None))
        )
        await session.execute(stmt)
