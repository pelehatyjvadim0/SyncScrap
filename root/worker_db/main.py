import json
import logging

from pydantic import HttpUrl, ValidationError

from root.persistence.connection import sessionmaker
from root.persistence.dao.books import BooksDAO
from root.persistence.dao.target_url import TargetUrlDAO
from root.shared.queues import EXTRACTED_DATA
from root.shared.rabbitmq import broker, faststream_app
from root.shared.schemas.book import SBookBase

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@broker.subscriber(queue=EXTRACTED_DATA)
async def handle_db(msg) -> None:
    raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
    payload = raw_payload if isinstance(raw_payload, dict) else json.loads(raw_payload)

    raw_page_url = payload.get("url")
    if not raw_page_url:
        logger.warning(" [DB] В сообщении нет url страницы — пропуск")
        return

    try:
        canonical_url = str(HttpUrl(raw_page_url))
    except Exception as exc:
        logger.warning(" [DB] Невалидный url страницы %r: %s", raw_page_url, exc)
        return

    items = payload.get("items") or []
    if not items:
        logger.info(
            " [DB] Пустой items для %s — только last_scraped_at (страница без товаров)",
            canonical_url,
        )

    async with sessionmaker() as session:
        try:
            for item in items:
                model = SBookBase(**item)
                book_data = model.model_dump(mode="json")
                book_data["extra"] = {
                    "image_url": item.get("image_url"),
                    "availability": item.get("availability"),
                    "source_page": canonical_url,
                }
                await BooksDAO.upsert_book(session, book_data)

            await TargetUrlDAO.mark_urls_scraped(session, [canonical_url])
            await session.commit()
            logger.info(
                " [DB] OK url=%s книг=%s last_scraped_at обновлён",
                canonical_url,
                len(items),
            )
        except ValidationError as exc:
            await session.rollback()
            logger.error(" [DB] Ошибка валидации книги: %s", exc)
            raise
        except Exception:
            await session.rollback()
            logger.exception(" [DB] Ошибка воркера записи в БД")
            raise
