from root.persistence.connection import sessionmaker
from root.shared.resources import res
from root.shared.redis_client import RedisManager
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession


class DependsGenerator:
    RESOURCES = res

    @staticmethod
    async def get_db():
        async with sessionmaker() as session:
            try:
                yield session
            except Exception:
                await session.rollback()

    @classmethod
    async def get_storage(cls):
        return await cls.RESOURCES.get_storage()


SessionDep = Annotated[AsyncSession, Depends(DependsGenerator.get_db)]
StorageDep = Annotated[RedisManager, Depends(DependsGenerator.get_storage)]
