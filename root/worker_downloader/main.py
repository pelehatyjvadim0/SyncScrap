from root.shared.rabbitmq import broker
from root.shared.queues import RAW_URLS, DOWNLOADED_PAGES
from root.shared.dependencies import StorageDep
from root.shared.config import settings
from root.worker_downloader.logic.utils import DownloaderUtils
import logging
from pydantic import ValidationError
from root.worker_downloader.logic.downloader import DownloaderLogic
from root.worker_downloader.dependencies import HttpClientDep
from root.shared.rabbitmq import faststream_app
from root.shared.schemas import RawUrlMessage

logger = logging.getLogger(__name__)


@broker.subscriber(RAW_URLS)
async def handle_url(msg, http_client: HttpClientDep, storage: StorageDep):
    url = None
    try:
        msg_data = msg.body.decode() if hasattr(msg, "body") else msg
        payload = {"url": msg_data.get('url')} if isinstance(msg_data, dict) else msg_data
        validated_message = RawUrlMessage.model_validate(payload)
        url = str(validated_message.url)
        logger.info(f" [→] URL получен: {url}")

        redis_key = await DownloaderUtils.get_url_hash(url)
        cached_html = await storage.get_html(redis_key)

        if cached_html is not None and msg_data.get('force_refresh') is False:
            logger.info(f" [↻] Найден HTML в Redis, повторная загрузка не требуется. URL: {url}")
        else:
            html = await DownloaderLogic.download_url(
                http_client=http_client,
                url=url,
                max_retries=settings.downloader.MAX_RETRIES,
                base_delay_seconds=settings.downloader.BASE_DELAY_SECONDS,
            )
            await DownloaderLogic.publish_in_storage(
                storage,
                redis_key,
                html,
                expire=settings.downloader.HTML_EXPIRE_SECONDS,
            )
            logger.info(f" [V] HTML успешно сохранен в Redis. URL: {url}")

        await broker.publish({"storage_key": redis_key, "url": url}, DOWNLOADED_PAGES)
        logger.info(
            f" [V] Страница обработана и отправлена в очередь `{DOWNLOADED_PAGES.name}`"
        )

    except ValidationError as e:
        logger.warning(" [!] Невалидное сообщение в RAW_URLS: %s", e.errors())
        return
    except Exception as e:
        logger.critical(
            f" [!] Ошибка Downloader Worker с {url if url else 'Неизвестный URL'}: {e}"
        )
        raise e
