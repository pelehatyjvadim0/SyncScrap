from typing import Annotated
from httpx import AsyncClient
from faststream import Depends
from root.shared.resources import res


class DependsGenerator:
    RESOURCES = res

    @classmethod
    async def get_http_client(cls):
        return await cls.RESOURCES.get_http_client()


HttpClientDep = Annotated[AsyncClient, Depends(DependsGenerator.get_http_client)]
