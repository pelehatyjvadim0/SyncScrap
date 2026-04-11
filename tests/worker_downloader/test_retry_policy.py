import httpx

from root.worker_downloader.logic.retry_policy import get_retry_delay, should_retry


def test_get_retry_delay_exponential_backoff() -> None:
    assert get_retry_delay(0.5, 1) == 0.5
    assert get_retry_delay(0.5, 2) == 1.0
    assert get_retry_delay(0.5, 3) == 2.0


def test_should_retry_for_connect_timeout() -> None:
    exc = httpx.ConnectTimeout("timeout")
    assert should_retry(exc, attempt=1, max_retries=3) is True


def test_should_not_retry_when_attempt_limit_reached() -> None:
    exc = httpx.ConnectError("network error")
    assert should_retry(exc, attempt=3, max_retries=3) is False


def test_should_retry_for_http_5xx() -> None:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(status_code=503, request=request)
    exc = httpx.HTTPStatusError("server error", request=request, response=response)
    assert should_retry(exc, attempt=1, max_retries=3) is True


def test_should_not_retry_for_http_4xx() -> None:
    request = httpx.Request("GET", "https://example.com")
    response = httpx.Response(status_code=404, request=request)
    exc = httpx.HTTPStatusError("not found", request=request, response=response)
    assert should_retry(exc, attempt=1, max_retries=3) is False
