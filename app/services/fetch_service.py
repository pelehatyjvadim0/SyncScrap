from httpx import AsyncClient
import logging
import httpx

logger = logging.getLogger(__name__)


class FetchService:
    @classmethod
    async def handle_url(cls, httpx_client: AsyncClient, url: str) -> str | None:
        try:
            response = await httpx_client.get(url, follow_redirects=True)
            if response.status_code == 200:
                html = response.text
                logger.info(f" [✓] Готово! Скачано {len(html)} байт с {url}")
                return html
            else:
                logger.warning(
                    f" [!] Сайт ответил статусом {response.status_code} . URL: {url}"
                )

        except httpx.ConnectError:
            logger.error(f" [x] Ошибка подключения к {url}")
            raise
        except httpx.ConnectTimeout:
            logger.error(f' [x] Ошибка по таймауту к {url}')
            raise
