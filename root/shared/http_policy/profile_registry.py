"""
Реестр HttpProfile по нормализованному hostname.

Встроенные сайты задаются в HttpProfileRegistry._preload_builtins: там же
связывается имя хоста с текущим объектом AvitoHttpProfile из profiles.py.
При смене полей в AvitoHttpProfile достаточно правки константы и перезапуска
процесса отдельной «перерегистрации» не нужно.
"""

from __future__ import annotations

from root.shared.http_policy.profiles import AvitoHttpProfile, HttpProfile
from root.shared.net.hostname import get_hostname


class HttpProfileRegistry:
    """Хранит соответствие нормализованный хост -> HttpProfile."""

    def __init__(self, *, preload_builtins: bool = True) -> None:
        self._by_host: dict[str, HttpProfile] = {}
        if preload_builtins:
            self._preload_builtins()

    def _preload_builtins(self) -> None:
        # Дефолтные площадки: одна строка на сайт, профиль импортируется из profiles.
        self.register("avito.ru", AvitoHttpProfile)

    @staticmethod
    def _normalize_host_key(hostname: str) -> str:
        key = hostname.strip().lower()
        if key.startswith("www."):
            key = key[4:]
        return key

    def register(self, hostname: str, profile: HttpProfile) -> None:
        """Добавить или заменить профиль для хоста (www снимается, lower)."""
        self._by_host[self._normalize_host_key(hostname)] = profile

    def for_hostname(self, hostname: str) -> HttpProfile | None:
        """Lookup по уже нормализованному хосту (как у get_hostname) или после normalize."""
        return self._by_host.get(self._normalize_host_key(hostname))

    def for_url(self, url: str) -> HttpProfile | None:
        """Hostname из URL через get_hostname, затем lookup."""
        host = get_hostname(url)
        if host is None:
            return None
        return self.for_hostname(host)


# Единый экземпляр для приложения; тесты могут подменить через register.
default_http_profile_registry = HttpProfileRegistry()


def register_host_profile(hostname: str, profile: HttpProfile) -> None:
    default_http_profile_registry.register(hostname, profile)


def profile_for_hostname(hostname: str) -> HttpProfile | None:
    return default_http_profile_registry.for_hostname(hostname)


def profile_for_url(url: str) -> HttpProfile | None:
    return default_http_profile_registry.for_url(url)
