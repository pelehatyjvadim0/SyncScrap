# Реестр HttpProfile по нормализованному hostname.
# Встроенные профили можно расширять через register() без изменения вызывающего кода.

from __future__ import annotations

from root.shared.http_policy.profiles import AvitoHttpProfile, HttpProfile
from root.shared.net.hostname import get_hostname, normalize_hostname


class HttpProfileRegistry:
    def __init__(self, *, preload_builtins: bool = True) -> None:
        self._by_host: dict[str, HttpProfile] = {}
        if preload_builtins:
            self._preload_builtins()

    def _preload_builtins(self) -> None:
        self.register("avito.ru", AvitoHttpProfile)

    def register(self, hostname: str, profile: HttpProfile) -> None:
        self._by_host[normalize_hostname(hostname)] = profile

    def for_hostname(self, hostname: str) -> HttpProfile | None:
        return self._by_host.get(normalize_hostname(hostname))

    def for_url(self, url: str) -> HttpProfile | None:
        host = get_hostname(url)
        if host is None:
            return None
        return self.for_hostname(host)


default_http_profile_registry = HttpProfileRegistry()
