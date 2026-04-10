import json
import logging

from pydantic import ValidationError

from root.shared.database.database_settings import sessionmaker
from root.shared.queues import EXTRACTED_DATA
from root.shared.rabbitmq import broker, faststream_app
from root.shared.schemas.book import SBookBase
from root.worker_db.crud.books_dao import BooksDAO

logger = logging.getLogger(__name__)


@broker.subscriber(queue=EXTRACTED_DATA)
async def handle_db(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)

    items = payload.get("items", [])
    if not items:
        logger.warning("No items received for DB worker")
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
                await BooksDAO.add_book(session, book_data)

            await session.commit()
            logger.info("Saved %s items to database", len(items))
        except ValidationError as exc:
            await session.rollback()
            logger.error("Book validation failed: %s", exc)
            raise
        except Exception:
            await session.rollback()
            logger.exception("Database worker failed")
            raise
