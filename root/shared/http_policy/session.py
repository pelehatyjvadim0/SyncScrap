# Фабрика долгоживущего AsyncSession: пул curl, таймаут ответа, дефолтный impersonate.
# Совпадение с первым запросом не обязательно: fetch_url может переопределить impersonate на get.

from typing import Any, cast

from curl_cffi.requests import AsyncSession
from curl_cffi.requests.impersonate import BrowserTypeLiteral

from root.shared.config import DownloaderSettings
from root.shared.http_policy.profiles import HttpProfile


class HTTPSessionFactory:

    def build(
        self,
        *,
        downloader_settings: DownloaderSettings,
        profile: HttpProfile | None = None,
    ) -> AsyncSession:
        # Собирает AsyncSession: max_clients, timeout чтения ответа, trust_env для прокси из env.
        impersonate = (
            profile.impersonate
            if profile is not None
            else downloader_settings.HTTP_IMPERSONATE
        )

        kwargs: dict[str, Any] = {
            "max_clients": downloader_settings.HTTP_MAX_CLIENTS,
            "impersonate": cast(BrowserTypeLiteral, impersonate),
            "timeout": downloader_settings.HTTP_TIMEOUT_SECONDS,
            "allow_redirects": True,
            "verify": True,
            "trust_env": True,
        }

        if profile is not None and profile.headers:
            kwargs["headers"] = profile.headers

        return AsyncSession(**kwargs)
