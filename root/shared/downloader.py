import asyncio
import logging

import httpx
from curl_cffi.requests import AsyncSession
from curl_cffi.requests import exceptions as cffi_req_exc

from root.shared.http_policy.request import fetch_url
from root.shared.http_policy.types import ProxyProviderProtocol
from root.shared.retry_policy import get_retry_delay, should_retry

logger = logging.getLogger(__name__)


class Downloader:
    @staticmethod
    async def fetch_html(
        http_client: AsyncSession,
        url: str,
        *,
        max_retries: int,
        base_delay_seconds: float,
        proxy_provider: ProxyProviderProtocol | None = None,
    ) -> str:
        for attempt in range(1, max_retries + 1):
            try:
                response = await fetch_url(
                    http_client,
                    url,
                    proxy_provider=proxy_provider,
                )
                response.raise_for_status()
                return response.text
            except Exception as exc:
                retry_allowed = should_retry(exc=exc, attempt=attempt, max_retries=max_retries)
                if not retry_allowed:
                    raise

                delay = get_retry_delay(base_delay_seconds, attempt)
                status_code = None
                if isinstance(exc, (httpx.HTTPStatusError, cffi_req_exc.HTTPError)):
                    status_code = exc.response.status_code
                logger.warning(
                    " [download] retry in %.2fs url=%s attempt=%s/%s status=%s error=%s",
                    delay,
                    url,
                    attempt,
                    max_retries,
                    status_code,
                    exc,
                )
                await asyncio.sleep(delay)

        raise RuntimeError(f"Failed to download URL after retries: {url}")
