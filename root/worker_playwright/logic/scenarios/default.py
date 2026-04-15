import logging

from playwright.async_api import Page

from root.shared.config import settings
from root.worker_playwright.logic.scenarios.base import SiteScenario

logger = logging.getLogger(__name__)


class DefaultScenario(SiteScenario):
    """Заглушка для неизвестных хостов: один переход и снимок DOM."""

    DOMAIN = "*"

    async def run(self, page: Page, url: str) -> str:
        timeout = settings.playwright_worker.NAVIGATION_TIMEOUT_MS
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        logger.debug(" [🎭] DefaultScenario: domcontentloaded url=%s", url)
        return await page.content()
