from typing import Any

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.models.listing_version import ListingVersion


class ListingVersionDAO:
    @staticmethod
    async def insert_version(session: AsyncSession, payload: dict[str, Any]) -> None:
        stmt = insert(ListingVersion).values(**payload)
        await session.execute(stmt)
