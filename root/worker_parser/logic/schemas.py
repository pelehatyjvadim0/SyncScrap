from typing import Protocol
from pydantic import BaseModel, HttpUrl
from decimal import Decimal


class BaseItemDTO(BaseModel):
    title: str
    price: Decimal
    currency: str
    image_url: HttpUrl | None
    url: HttpUrl
    availability: bool


class DownloadedPageMessage(BaseModel):
    storage_key: str
    url: HttpUrl


class ExtractedDataMessage(BaseModel):
    url: HttpUrl
    items: list[BaseItemDTO]


class StorageProtocol(Protocol):
    async def get_html(self, key: str) -> str | None: ...
