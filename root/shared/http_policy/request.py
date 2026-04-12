"""
Один HTTP GET под политику: профиль (impersonate, headers), jitter, прокси на запрос.
Anti-fraud - случайная пауза перед запросом и браузерный TLS-отпечаток (curl_cffi impersonate).
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Literal, cast

from curl_cffi.requests import AsyncSession
from curl_cffi.requests.impersonate import BrowserTypeLiteral
from curl_cffi.requests.models import Response

from root.shared.config import settings
from root.shared.http_policy.profiles import HttpProfile
from root.shared.http_policy.profile_registry import profile_for_url
from root.shared.http_policy.proxy import NoProxyProvider
from root.shared.http_policy.types import ProxyProviderProtocol
from root.shared.net.timeout import random_delay_in_jitter_range

logger = logging.getLogger(__name__)


def _default_profile_from_settings() -> HttpProfile:
    # Fallback если хост не в реестре - настройки воркера из env (DOWNLOADER_*).
    d = settings.downloader
    return HttpProfile(
        impersonate=d.HTTP_IMPERSONATE,
        jitter_min_seconds=d.HTTP_JITTER_TIMEOUT_MIN_SECONDS,
        jitter_max_seconds=d.HTTP_JITTER_TIMEOUT_MAX_SECONDS,
    )


def resolve_effective_profile(
    url: str,
    explicit: HttpProfile | None,
) -> tuple[HttpProfile, Literal["explicit", "registry", "default"]]:
    # Явный profile, иначе реестр по URL, иначе дефолт из settings.downloader.
    if explicit is not None:
        return explicit, "explicit"
    from_registry = profile_for_url(url)
    if from_registry is not None:
        return from_registry, "registry"
    return _default_profile_from_settings(), "default"


async def _sleep_jitter(profile: HttpProfile) -> None:
    # Случайная задержка в [min, max] из профиля перед GET.
    delay = random_delay_in_jitter_range(
        profile.jitter_min_seconds,
        profile.jitter_max_seconds,
    )
    logger.debug(
        "http_policy jitter: спим %.3fs (profile impersonate=%s)",
        delay,
        profile.impersonate,
    )
    await asyncio.sleep(delay)


def _build_get_kwargs(
    *,
    impersonate: BrowserTypeLiteral,
    headers: dict[str, str] | None,
    proxy_url: str | None,
) -> dict[str, Any]:
    # Аргументы для session.get: allow_redirects, impersonate, опционально headers и proxy.
    kwargs: dict[str, Any] = {
        "allow_redirects": True,
        "impersonate": impersonate,
    }
    if headers:
        kwargs["headers"] = headers
    if proxy_url is not None:
        kwargs["proxy"] = proxy_url
    return kwargs


async def fetch_url(
    session: AsyncSession,
    url: str,
    *,
    proxy_provider: ProxyProviderProtocol | None = None,
    profile: HttpProfile | None = None,
) -> Response:
    # Цепочка: effective profile, jitter sleep, proxy, затем session.get.
    effective, source = resolve_effective_profile(url, profile)
    logger.debug(
        "http_policy fetch: profile_source=%s impersonate=%s",
        source,
        effective.impersonate,
    )

    impersonate = cast(BrowserTypeLiteral, effective.impersonate)
    header_map = effective.headers if effective.headers else None

    await _sleep_jitter(effective)

    provider = proxy_provider if proxy_provider is not None else NoProxyProvider()
    proxy_url = await provider.get_proxy()
    if proxy_url:
        logger.debug("http_policy fetch: Используем прокси для этого запроса")

    kwargs = _build_get_kwargs(
        impersonate=impersonate,
        headers=header_map,
        proxy_url=proxy_url,
    )
    return await session.get(url, **kwargs)
