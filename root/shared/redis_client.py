import redis.asyncio as redis
from root.shared.config import settings


class RedisManager:
    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        self.redis = redis.from_url(
            settings.redis.REDIS_URL, encoding="utf-8", decode_responses=True
        )

    async def set_nx_ttl(self, key: str, ttl: int) -> bool:
        if self.redis is None:
            return False
        return await self.redis.set(key, "1", ex=ttl, nx=True)

    async def set_html(self, key: str, html: str, expire: int = 600):
        if self.redis is None:
            raise RuntimeError("Redis client is not connected")
        await self.redis.set(f'page:{key}', html, ex=expire)
        
    async def get_html(self, key: str) -> str | None:
        if self.redis is None:
            raise RuntimeError("Redis client is not connected")
        return await self.redis.get(f"page:{key}")
    
    async def delete_html(self, key: str):
        if self.redis is None:
            raise RuntimeError("Redis client is not connected")
        await self.redis.delete(f'page:{key}')
        
    async def close(self):
        if self.redis:
            await self.redis.close()
            
redis_manager = RedisManager()
