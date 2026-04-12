# Контракт поставщика прокси для fetch_url. None - ходить без прокси на этом запросе.

from typing import Protocol


class ProxyProviderProtocol(Protocol):
    async def get_proxy(self) -> str | None:
        ...
