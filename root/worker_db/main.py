import json
import logging

from pydantic import ValidationError

from root.persistence.connection import sessionmaker
from root.persistence.dao.books import BooksDAO
from root.shared.queues import EXTRACTED_DATA
from root.shared.rabbitmq import broker, faststream_app
from root.shared.schemas.book import SBookBase

logger = logging.getLogger(__name__)


@broker.subscriber(queue=EXTRACTED_DATA)
async def handle_db(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)

    items = payload.get("items", [])
    if not items:
        logger.warning(" [DB] Пустой список items в EXTRACTED_DATA — пропуск")
        return

    async with sessionmaker() as session:
        try:
            for item in items:
                model = SBookBase(**item)
                book_data = model.model_dump(mode="json")
                book_data["extra"] = {
                    "image_url": item.get("image_url"),
                    "availability": item.get("availability"),
                    "source_page": payload.get("url"),
                }
                await BooksDAO.upsert_book(session, book_data)

            await session.commit()
            logger.info(" [DB] Сохранено в БД записей (items): %s", len(items))
        except ValidationError as exc:
            await session.rollback()
            logger.error(" [DB] Ошибка валидации книги: %s", exc)
            raise
        except Exception:
            await session.rollback()
            logger.exception(" [DB] Ошибка воркера записи в БД")
            raise
