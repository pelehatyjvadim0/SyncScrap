from root.worker_parser.logic.schemas import BaseItemDTO
from abc import ABC, abstractmethod


class BaseParser(ABC):
    DOMAIN: str = ""

    @abstractmethod
    async def parse(self, html: str, url: str) -> list[BaseItemDTO]:
        raise NotImplementedError
