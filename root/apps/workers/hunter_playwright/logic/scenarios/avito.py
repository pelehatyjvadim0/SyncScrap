
# Сценарий для avito.ru - доработать навигацию, ожидания, скролл и т.д.

# Сейчас: минимальный переход + HTML (чтобы пайплайн можно было проверить).

import logging

from playwright.async_api import Page

from root.shared.config import settings
from root.apps.workers.hunter_playwright.logic.scenarios.base import SiteScenario

logger = logging.getLogger(__name__)


class AvitoScenario(SiteScenario):
    DOMAIN = "avito.ru"

    async def run(self, page: Page, url: str) -> str:
        timeout = settings.playwright_worker.NAVIGATION_TIMEOUT_MS
        # TODO: имитация пользователя, ожидание селекторов, обход капчи и т.п.
        await page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        logger.info(" [🎭] AvitoScenario: базовая загрузка (доработай run()) url=%s", url)
        return await page.content()
