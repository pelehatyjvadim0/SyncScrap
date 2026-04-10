from httpx import AsyncClient
import asyncio
import logging
import httpx
from root.worker_downloader.logic.retry_policy import get_retry_delay, should_retry
from root.worker_downloader.logic.schemas import StorageProtocol

logger = logging.getLogger(__name__)


class DownloaderLogic:
    async def _handle_download_error(
        exc: Exception,
        url: str,
        attempt: int,
        max_retries: int,
        base_delay_seconds: float,
    ) -> None:
        is_retry_allowed = should_retry(
            exc=exc,
            attempt=attempt,
            max_retries=max_retries,
        )

        if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout)):
            if not is_retry_allowed:
                logger.error(
                    " [x] Сетевая ошибка после %s попыток. url=%s ошибка=%s",
                    max_retries,
                    url,
                    exc,
                )
                raise exc

            delay = get_retry_delay(base_delay_seconds, attempt)
            logger.warning(
                " [~] Сетевая ошибка, повтор через %.2f сек. url=%s попытка=%s/%s ошибка=%s",
                delay,
                url,
                attempt,
                max_retries,
                exc,
            )
            await asyncio.sleep(delay)
            return

        if isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code

            # Для 4xx повтор обычно бессмысленен: ошибка запроса/ресурса.
            if 400 <= status_code < 500:
                logger.error(
                    " [!] HTTP %s без повторной попытки. url=%s",
                    status_code,
                    url,
                )
                raise exc

            if not is_retry_allowed:
                logger.error(
                    " [x] HTTP %s после %s попыток. url=%s",
                    status_code,
                    max_retries,
                    url,
                )
                raise exc

            delay = get_retry_delay(base_delay_seconds, attempt)
            logger.warning(
                " [~] HTTP %s, повтор через %.2f сек. url=%s попытка=%s/%s",
                status_code,
                delay,
                url,
                attempt,
                max_retries,
            )
            await asyncio.sleep(delay)
            return

        raise exc

    @staticmethod
    def _handle_storage_error(exc: Exception, redis_key: str) -> None:
        logger.critical(
            " [!] Критическая ошибка сохранения HTML в Redis. ключ=%s ошибка=%s",
            redis_key,
            exc,
        )
        raise exc

    @staticmethod
    async def download_url(
        httpx_client: AsyncClient,
        url: str,
        max_retries: int = 3,
        base_delay_seconds: float = 0.5,
    ) -> str:
        for attempt in range(1, max_retries + 1):
            try:
                response = await httpx_client.get(url, follow_redirects=True)
                response.raise_for_status()

                html = response.text
                logger.debug(
                    " [✓] HTML успешно загружен. url=%s размер=%s попытка=%s",
                    url,
                    len(html),
                    attempt,
                )
                return html

            except Exception as exc:
                await DownloaderLogic._handle_download_error(
                    exc=exc,
                    url=url,
                    attempt=attempt,
                    max_retries=max_retries,
                    base_delay_seconds=base_delay_seconds,
                )

        raise RuntimeError(f"Не удалось загрузить страницу: {url}")

    @staticmethod
    async def publish_in_storage(
        storage_client: StorageProtocol, redis_key: str, html: str, expire: int
    ):
        try:
            await storage_client.set_html(key=redis_key, html=html, expire=expire)
        except Exception as exc:
            DownloaderLogic._handle_storage_error(exc=exc, redis_key=redis_key)
