from __future__ import annotations

from curl_cffi.requests import AsyncSession

from root.shared.config import settings
from root.shared.http_policy.session import HTTPSessionFactory
from root.shared.redis_client import RedisManager


def build_scrape_async_session() -> AsyncSession:
    """Один экземпляр AsyncSession для загрузки HTML: impersonate, таймауты, редиректы."""
    return HTTPSessionFactory().build(
        downloader_settings=settings.downloader,
        profile=None,
    )


class Resources:
    def __init__(self) -> None:
        self.http_client: AsyncSession | None = None
        self.storage: RedisManager | None = None

    async def init_all(self) -> None:
        if self.http_client is None:
            self.http_client = build_scrape_async_session()
        if self.storage is None:
            self.storage = RedisManager()
            await self.storage.connect()

    async def close_all(self) -> None:
        if self.http_client is not None:
            await self.http_client.close()
            self.http_client = None
        if self.storage is not None:
            await self.storage.close()
            self.storage = None

    async def get_http_client(self) -> AsyncSession:
        if self.http_client is None:
            await self.init_all()
        assert self.http_client is not None
        return self.http_client

    async def get_storage(self) -> RedisManager:
        if self.storage is None:
            await self.init_all()
        assert self.storage is not None
        return self.storage


res = Resources()
