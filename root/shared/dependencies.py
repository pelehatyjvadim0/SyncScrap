from typing import Annotated

from fastapi import Depends

from root.shared.redis_client import RedisManager
from root.shared.resources import res


class DependsGenerator:
    RESOURCES = res

    @classmethod
    async def get_storage(cls):
        return await cls.RESOURCES.get_storage()

    @classmethod
    async def get_db(cls):
        from root.persistence.relational_store.connection import sessionmaker
        async with sessionmaker() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()


StorageDep = Annotated[RedisManager, Depends(DependsGenerator.get_storage)]
