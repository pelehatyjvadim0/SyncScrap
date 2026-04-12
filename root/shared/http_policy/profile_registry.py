# Реестр HttpProfile по нормализованному hostname.
# Встроенные сайты - HttpProfileRegistry._preload_builtins связывает хост с AvitoHttpProfile из profiles.
# Смена полей в AvitoHttpProfile - правка константы и перезапуск, отдельная перерегистрация не нужна.

from __future__ import annotations

from root.shared.http_policy.profiles import AvitoHttpProfile, HttpProfile
from root.shared.net.hostname import get_hostname, normalize_hostname


class HttpProfileRegistry:
    # Нормализованный хост - HttpProfile

    def __init__(self, *, preload_builtins: bool = True) -> None:
        self._by_host: dict[str, HttpProfile] = {}
        if preload_builtins:
            self._preload_builtins()

    def _preload_builtins(self) -> None:
        # Одна строка на сайт - профиль из profiles
        self.register("avito.ru", AvitoHttpProfile)

    def register(self, hostname: str, profile: HttpProfile) -> None:
        # Добавить или заменить профиль - нормализация через net.hostname
        self._by_host[normalize_hostname(hostname)] = profile

    def for_hostname(self, hostname: str) -> HttpProfile | None:
        # Lookup по хосту после normalize_hostname
        return self._by_host.get(normalize_hostname(hostname))

    def for_url(self, url: str) -> HttpProfile | None:
        # get_hostname затем lookup
        host = get_hostname(url)
        if host is None:
            return None
        return self.for_hostname(host)


# Один экземпляр на процесс - регистрация через .register()
default_http_profile_registry = HttpProfileRegistry()
