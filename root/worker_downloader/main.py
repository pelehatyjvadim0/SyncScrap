import logging

from pydantic import ValidationError

from root.shared.dependencies import StorageDep
from root.shared.rabbitmq import broker, faststream_app
from root.worker_downloader.dependencies import HttpClientDep
from root.shared.queues import RAW_URLS
from root.worker_downloader.logic.download_workflow import DownloadWorkflow
from root.worker_downloader.logic.message_payload import RawUrlPayloadError

logger = logging.getLogger(__name__)


@broker.subscriber(RAW_URLS)
async def handle_url(msg, http_client: HttpClientDep, storage: StorageDep) -> None:
    url_for_log = "?"
    try:
        workflow = DownloadWorkflow(http_client, storage)
        await workflow.run(msg)
    except RawUrlPayloadError as exc:
        logger.warning(" [↓] RAW_URLS: %s", exc)
    except ValidationError as exc:
        logger.warning(" [↓] Невалидное RAW_URLS (Pydantic): %s", exc.errors())
    except Exception as exc:
        logger.critical(
            " [↓] Критическая ошибка downloader: %s",
            exc,
            exc_info=True,
        )
        raise
