from typing import Protocol


class StorageProtocol(Protocol):
    async def set_html(self, key: str, html: str, expire: int = 600) -> None: ...

    async def get_html(self, key: str) -> str | None: ...
