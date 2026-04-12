import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.models.listing import Listing

logger = logging.getLogger(__name__)


class ListingDAO:
    @classmethod
    async def upsert_listing(
        cls, session: AsyncSession, listing_data: dict[str, Any]
    ) -> int | None:
        stmt = insert(Listing).values(**listing_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_={
                "title": stmt.excluded.title,
                "price": stmt.excluded.price,
                "currency": stmt.excluded.currency,
                "extra": stmt.excluded.extra,
                "updated_at": func.now(),
            },
        ).returning(Listing.id)

        result = await session.execute(stmt)
        row_id = result.scalar_one_or_none()
        logger.debug(
            " [DB] upsert listings: url=%s id=%s",
            listing_data.get("url"),
            row_id,
        )
        return row_id
