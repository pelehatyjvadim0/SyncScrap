from typing import Annotated

from fastapi import Depends
from curl_cffi.requests import AsyncSession

from root.shared.resources import res


class DependsGenerator:
    RESOURCES = res

    @classmethod
    async def get_http_client(cls):
        return await cls.RESOURCES.get_http_client()


HttpClientDep = Annotated[AsyncSession, Depends(DependsGenerator.get_http_client)]
