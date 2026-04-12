import httpx
from curl_cffi.requests import exceptions as cffi_req_exc


def get_retry_delay(base_delay_seconds: float, attempt: int) -> float:
    return base_delay_seconds * (2 ** (attempt - 1))


def should_retry(exc: Exception, attempt: int, max_retries: int) -> bool:
    if attempt >= max_retries:
        return False

    if isinstance(
        exc,
        (
            httpx.ConnectError,
            httpx.ConnectTimeout,
            cffi_req_exc.ConnectionError,
            cffi_req_exc.ConnectTimeout,
            cffi_req_exc.DNSError,
        ),
    ):
        return True

    if isinstance(exc, (httpx.HTTPStatusError, cffi_req_exc.HTTPError)):
        status_code = exc.response.status_code
        return 500 <= status_code < 600

    return False
