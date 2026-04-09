from app.dao.books_dao import BooksDAO
from app.core.dependencies import DependsGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import logging
from app.schemas.book import SBookBase

logger = logging.getLogger(__name__)


class BooksService:
    @classmethod
    async def add_books(cls, session: AsyncSession, book_model: SBookBase):
        book_data = book_model.model_dump(mode="json")
        return await BooksDAO.add_book(session, book_data)
