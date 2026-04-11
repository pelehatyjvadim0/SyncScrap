from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient

from root.shared.resources import res


class DependsGenerator:
    RESOURCES = res

    @classmethod
    async def get_http_client(cls):
        return await cls.RESOURCES.get_http_client()


HttpClientDep = Annotated[AsyncClient, Depends(DependsGenerator.get_http_client)]
