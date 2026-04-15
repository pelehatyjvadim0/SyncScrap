import logging

from pydantic import ValidationError

from root.shared.queues import EXTRACTION_URLS, RAW_URLS_PLAYWRIGHT
from root.shared.rabbitmq import broker, faststream_app
from root.shared.schemas.pipeline_messages import ExtractionTask
from root.worker_playwright.dependencies import pw_res
from root.worker_playwright.logic.message_payload import RawUrlPayloadError
from root.worker_playwright.logic.workflow import PlaywrightWorkflow

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@faststream_app.after_startup
async def _playwright_startup() -> None:
    await pw_res.init_all()
    logger.info(" [🎭] Ресурсы worker_playwright инициализированы")


@faststream_app.on_shutdown
async def _playwright_shutdown() -> None:
    await pw_res.close_all()
    logger.info(" [🎭] Ресурсы worker_playwright закрыты")


@broker.subscriber(RAW_URLS_PLAYWRIGHT)
async def handle_playwright_url(msg) -> None:
    try:
        storage = await pw_res.get_storage()
        browser = await pw_res.get_browser()
        workflow = PlaywrightWorkflow(browser, storage)
        await workflow.run(msg)
    except RawUrlPayloadError as exc:
        logger.warning(" [🎭] raw_urls_playwright: %s", exc)
    except ValidationError as exc:
        logger.warning(" [🎭] Невалидное сообщение: %s", exc.errors())
    except Exception as exc:
        logger.critical(
            " [🎭] Критическая ошибка worker_playwright: %s",
            exc,
            exc_info=True,
        )
        raise


@broker.subscriber(EXTRACTION_URLS)
async def handle_extraction_task(msg) -> None:
    try:
        raw_payload = msg.body.decode() if hasattr(msg, "body") else msg
        task = ExtractionTask.model_validate_json(raw_payload) if isinstance(raw_payload, str) else ExtractionTask.model_validate(raw_payload)
        storage = await pw_res.get_storage()
        browser = await pw_res.get_browser()
        workflow = PlaywrightWorkflow(browser, storage)
        await workflow.run_extraction_task(task)
    except Exception as exc:
        logger.critical(" [🎭] extraction task failed: %s", exc, exc_info=True)
        raise
