import httpx


def get_retry_delay(base_delay_seconds: float, attempt: int) -> float:
    return base_delay_seconds * (2 ** (attempt - 1))


def should_retry(exc: Exception, attempt: int, max_retries: int) -> bool:
    if attempt >= max_retries:
        return False

    if isinstance(exc, (httpx.ConnectError, httpx.ConnectTimeout)):
        return True

    if isinstance(exc, httpx.HTTPStatusError):
        status_code = exc.response.status_code
        return 500 <= status_code < 600

    return False
