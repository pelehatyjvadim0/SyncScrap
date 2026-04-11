import logging

from root.shared.rabbitmq import broker, faststream_app, router
from root.shared.dependencies import StorageDep
from pydantic import ValidationError
from root.worker_parser.logic.coordinator import ParserCoordinator
from root.worker_parser.logic.service import ParserService
from root.shared.queues import DOWNLOADED_PAGES, EXTRACTED_DATA

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)
coordinator = ParserCoordinator()


@router.subscriber(DOWNLOADED_PAGES)
async def handle_url(msg, storage: StorageDep):
    try:
        message = ParserService.parse_downloaded_message(msg)
        logger.info(" [→] Получена задача на парсинг. URL: %s", message.url)

        result = await ParserService.parse_page(message, storage, coordinator)
        broker_payload = ParserService.serialize_for_broker(result)
        await broker.publish(message=broker_payload, queue=EXTRACTED_DATA)

        logger.info(
            " [✓] Парсинг завершен. URL: %s | Товаров: %s",
            result.url,
            len(result.items),
        )

    except ValidationError as exc:
        logger.warning(" [!] Невалидное сообщение в DOWNLOADED_PAGES: %s", exc.errors())
        return
    except ValueError as exc:
        logger.warning(" [!] Задача отклонена: %s", exc)
        return
    except Exception as exc:
        logger.critical(" [!] Критическая ошибка parser-воркера: %s", exc, exc_info=True)
        raise exc
