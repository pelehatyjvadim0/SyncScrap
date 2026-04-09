from app.core.rabbitmq import broker, faststream_app
from app.core.queues import URLS_QUEUE, DAO_QUEUE
import logging
from app.services.fetch_service import FetchService
from app.services.scraped_service import ScrapedService
import httpx

logger = logging.getLogger(__name__)

httpx_client = None

@faststream_app.on_startup
async def setup_client():
    limit = httpx.Limits(max_connections=50, max_keepalive_connections=20)
    timeout = httpx.Timeout(20.0, connect=10.0)
    
    global httpx_client
    httpx_client = httpx.AsyncClient(limits=limit, timeout=timeout)
    logger.info(" [V] Воркер запустил свой HTTPX клиент")

@faststream_app.on_shutdown
async def close_client():
    global httpx_client
    if httpx_client:
        await httpx_client.aclose()
        logger.info(" [V] Воркер закрыл HTTPX клиент")


@broker.subscriber(URLS_QUEUE)
async def handle_url(msg):
    global httpx_client
    if httpx_client is None:
        logger.error("КЛИЕНТ НЕ ИНИЦИАЛИЗИРОВАН")
        return

    try:
        url = msg.body.decode()

        logger.info(f" [→] Воркер взял URL: {url}")

        html = await FetchService.handle_url(httpx_client, url)
        if not html:
            logger.error(f" [!] Не удалось получить html | URL: {url}")
            return

        scraped_dict = await ScrapedService.scrap_book_html(html)
        if not scraped_dict:
            logger.error(f" [!] Не удалось заскрапить html! URL: {url}")
            return

        scraped_dict["url"] = url

        try:
            await broker.publish(scraped_dict, DAO_QUEUE)
            logger.info(" [+] Данные успешно добавлены в очередь к БД")
        except Exception as e:
            logger.error(f" [!] Ошибка отправки готовых данных в очередь к БД: {e}")
            raise e
    except Exception as e:
        logger.critical(f" [!] Критическая ошибка в работе воркера: {e}", exc_info=True)
        raise e
