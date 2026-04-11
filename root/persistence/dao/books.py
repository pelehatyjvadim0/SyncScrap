import logging
from typing import Any

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.models.books import Books

logger = logging.getLogger(__name__)


class BooksDAO:
    @classmethod
    async def upsert_book(cls, session: AsyncSession, book_data: dict[str, Any]) -> int | None:
        stmt = insert(Books).values(**book_data)
        stmt = stmt.on_conflict_do_update(
            index_elements=["url"],
            set_={
                "title": stmt.excluded.title,
                "price": stmt.excluded.price,
                "currency": stmt.excluded.currency,
                "extra": stmt.excluded.extra,
                "updated_at": func.now(),
            },
        ).returning(Books.id)

        result = await session.execute(stmt)
        book_id = result.scalar_one_or_none()
        logger.debug(
            " [DB] upsert books: url=%s id=%s",
            book_data.get("url"),
            book_id,
        )
        return book_id
