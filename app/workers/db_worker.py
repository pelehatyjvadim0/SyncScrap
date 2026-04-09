from app.core.rabbitmq import broker
from app.core.queues import DAO_QUEUE
from app.core.dependencies import DependsGenerator
from app.services.books_service import BooksService
from pydantic import ValidationError
import json
import logging
from app.schemas.book import SBookBase

logger = logging.getLogger(__name__)


@broker.subscriber(queue=DAO_QUEUE)
async def handle_db(msg):
    scraped_dict = json.loads(msg.body.decode())

    try:
        book_model = SBookBase(**scraped_dict)
    except ValidationError as e:
        logger.critical(f" [!] Ошибка валидации данных книги: {e.errors()}")
        return
    except Exception as e:
        logger.critical(f" [!] Незвестная ошибка при создании модели: {e}")
        return

    db_gen = DependsGenerator.get_db()
    try:
        async for session in db_gen:
            try:
                book_id = await BooksService.add_books(session, book_model)
                if not book_id:
                    logger.info(" [!] Попытка вставить дубликат в базу, пропускаю...")
                await session.commit()
            except Exception as e:
                logger.critical(
                    f" [!] Неизвестная ошибка при сохранении данных в БД: {e}"
                )
                await session.rollback()
                return
    except Exception as e:
        logger.critical(f" [!] Неизвестная ошибка при работе с сессией БД: {e}")
        return

    logger.info(f" [V] Данные успешно укомплектованы в базе! ID: {book_id}")
