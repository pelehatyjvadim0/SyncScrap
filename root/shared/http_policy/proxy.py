# Прокси на один запрос - proxy в get, не в session.proxy.

import random

from root.shared.http_policy.types import ProxyProviderProtocol


class NoProxyProvider(ProxyProviderProtocol):
    async def get_proxy(self) -> str | None:
        return None


class RandomProxyProvider(ProxyProviderProtocol):
    def __init__(self, proxy_url_list: list[str]) -> None:
        self.proxy_url_list = proxy_url_list

    async def get_proxy(self) -> str | None:
        if not self.proxy_url_list:
            return None
        return random.choice(self.proxy_url_list)
