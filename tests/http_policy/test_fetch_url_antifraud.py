# fetch_url - цепочка jitter sleep и вызов session.get с impersonate из выбранного профиля.
# curl_cffi не ходит в сеть - мокаем session.get и asyncio.sleep.

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from root.shared.http_policy.request import fetch_url


@patch("root.shared.http_policy.request.asyncio.sleep", new_callable=AsyncMock)
def test_fetch_url_calls_sleep_before_get(mock_sleep):
    # Anti-fraud пауза перед запросом - sleep вызывается один раз
    session = MagicMock()
    session.get = AsyncMock(return_value=MagicMock())

    async def run():
        await fetch_url(session, "https://books.toscrape.com/catalogue/")

    asyncio.run(run())

    mock_sleep.assert_awaited_once()
    session.get.assert_awaited_once()


@patch("root.shared.http_policy.request.asyncio.sleep", new_callable=AsyncMock)
def test_fetch_url_passes_impersonate_to_get(mock_sleep):
    # В kwargs get должен быть impersonate - иначе curl не меняет TLS fingerprint на запросе
    session = MagicMock()
    session.get = AsyncMock(return_value=MagicMock())

    async def run():
        await fetch_url(session, "https://books.toscrape.com/")

    asyncio.run(run())

    _args, kwargs = session.get.call_args
    assert kwargs.get("allow_redirects") is True
    assert "impersonate" in kwargs
    assert kwargs["impersonate"] is not None
