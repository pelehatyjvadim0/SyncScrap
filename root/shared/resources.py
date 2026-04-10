from httpx import AsyncClient
import httpx
from root.shared.redis_client import RedisManager


class Resources:
    # Глобальный контейнер для тяжёлых ресурсов
    def __init__(self):
        self.http_client: AsyncClient | None = None
        self.storage: RedisManager | None = None

    async def init_all(self):
        if self.http_client is None:
            self.http_client = AsyncClient(
                limits=httpx.Limits(max_connections=50),
                timeout=httpx.Timeout(20.0, connect=15.0),
            )
        if self.storage is None:
            self.storage = RedisManager()
            await self.storage.connect()

    async def close_all(self):
        if self.http_client:
            await self.http_client.aclose()
        if self.storage:
            await self.storage.close()

    async def get_http_client(self):
        if self.http_client is None:
            await self.init_all()
        return self.http_client

    async def get_storage(self):
        if self.storage is None:
            await self.init_all()
        return self.storage


res = Resources()
