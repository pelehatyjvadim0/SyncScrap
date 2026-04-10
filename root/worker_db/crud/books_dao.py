from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.worker_db.models.books import Books


class BooksDAO:
    @classmethod
    async def add_book(cls, session: AsyncSession, book_data: dict):
        stmt = insert(Books).values(**book_data)

        stmt = stmt.on_conflict_do_nothing(index_elements=["url"]).returning(Books.id)

        result = await session.execute(stmt)

        book_id = result.scalar_one_or_none()
        return book_id
