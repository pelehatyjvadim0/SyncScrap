# Реестр профилей по хосту и resolve_effective_profile - три источника - explicit, registry, default.
# Anti-fraud настройки берутся из профиля выбранного источника.

import pytest

from root.shared.config import settings
from root.shared.http_policy.profiles import AvitoHttpProfile, HttpProfile
from root.shared.http_policy.profile_registry import HttpProfileRegistry, default_http_profile_registry
from root.shared.http_policy.request import resolve_effective_profile


def test_registry_avito_host_returns_bundled_profile():
    # Встроенный avito.ru в default registry совпадает с константой из profiles
    p = default_http_profile_registry.for_url("https://www.avito.ru/item/1")
    assert p is not None
    assert p is AvitoHttpProfile
    assert p.impersonate == "chrome131"


def test_registry_unknown_host_returns_none_before_resolve():
    # Нет записи - for_url отдаёт None, дальше подставится default в resolve
    assert default_http_profile_registry.for_url("https://books.toscrape.com/") is None


def test_registry_clean_instance_without_builtins_register_manually():
    # Изолированный реестр для теста - без побочных эффектов на глобальный default
    reg = HttpProfileRegistry(preload_builtins=False)
    custom = HttpProfile(
        impersonate="edge99",
        jitter_min_seconds=0.1,
        jitter_max_seconds=0.2,
    )
    reg.register("example.test", custom)
    assert reg.for_url("https://www.example.test/path") is custom


def test_resolve_explicit_wins_over_registry():
    # Явный профиль - источник explicit даже для avito URL
    explicit = HttpProfile(
        impersonate="chrome120",
        jitter_min_seconds=0.0,
        jitter_max_seconds=0.0,
    )
    prof, source = resolve_effective_profile("https://avito.ru/", explicit)
    assert source == "explicit"
    assert prof is explicit


def test_resolve_registry_for_avito_when_no_explicit():
    prof, source = resolve_effective_profile("https://avito.ru/x", None)
    assert source == "registry"
    assert prof is AvitoHttpProfile


def test_resolve_default_for_unknown_host_matches_downloader_settings():
    # Нет в реестре - дефолт из settings.downloader - те же поля что и в конфиге воркера
    prof, source = resolve_effective_profile("https://books.toscrape.com/", None)
    assert source == "default"
    d = settings.downloader
    assert prof.impersonate == d.HTTP_IMPERSONATE
    assert prof.jitter_min_seconds == d.HTTP_JITTER_TIMEOUT_MIN_SECONDS
    assert prof.jitter_max_seconds == d.HTTP_JITTER_TIMEOUT_MAX_SECONDS
