from abc import ABC, abstractmethod

from playwright.async_api import Page


class SiteScenario(ABC):
    # Сценарий навигации для домена: из Page получить итоговый HTML.

    DOMAIN: str = ""

    @abstractmethod
    async def run(self, page: Page, url: str) -> str:
        raise NotImplementedError
