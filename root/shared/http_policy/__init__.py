"""
HTTP policy для скрапинга: curl_cffi impersonate, реестр профилей по хосту,
случайная пауза jitter перед GET, прокси только на запрос (без мутации сессии).

Публичные точки: fetch_url, HTTPSessionFactory, HttpProfile, profile_for_url,
register_host_profile.
"""

from root.shared.http_policy.profiles import HttpProfile
from root.shared.http_policy.profile_registry import (
    HttpProfileRegistry,
    default_http_profile_registry,
    profile_for_hostname,
    profile_for_url,
    register_host_profile,
)
from root.shared.http_policy.request import fetch_url, resolve_effective_profile
from root.shared.http_policy.session import HTTPSessionFactory

__all__ = [
    "HttpProfile",
    "HttpProfileRegistry",
    "HTTPSessionFactory",
    "default_http_profile_registry",
    "fetch_url",
    "profile_for_hostname",
    "profile_for_url",
    "register_host_profile",
    "resolve_effective_profile",
]
