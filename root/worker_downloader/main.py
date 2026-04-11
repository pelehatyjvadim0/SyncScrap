import logging

from pydantic import ValidationError

from root.shared.dependencies import StorageDep
from root.shared.rabbitmq import faststream_app, router
from root.worker_downloader.dependencies import HttpClientDep
from root.shared.queues import RAW_URLS
from root.worker_downloader.logic.download_workflow import DownloadWorkflow
from root.worker_downloader.logic.message_payload import RawUrlPayloadError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@router.subscriber(RAW_URLS)
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
