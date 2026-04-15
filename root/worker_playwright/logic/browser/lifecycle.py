import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from playwright.async_api import Browser, Page, Playwright, async_playwright

from root.shared.config import settings
from root.worker_playwright.logic.browser.context_factory import new_context_kwargs

logger = logging.getLogger(__name__)


class BrowserLifecycle:
    # Один Playwright + один Chromium; на задачу — новый BrowserContext + Page.

    def __init__(self) -> None:
        self._pw: Playwright | None = None
        self._browser: Browser | None = None

    async def start(self) -> None:
        if self._browser is not None:
            return
        logger.info(" [🎭] Запуск Playwright (Chromium)...")
        pw = await async_playwright().start()
        self._pw = pw
        headless = settings.playwright_worker.HEADLESS
        self._browser = await pw.chromium.launch(headless=headless)
        logger.info(" [🎭] Chromium готов (headless=%s)", headless)

    async def stop(self) -> None:
        if self._browser is not None:
            await self._browser.close()
            self._browser = None
        if self._pw is not None:
            await self._pw.stop()
            self._pw = None
        logger.info(" [🎭] Playwright остановлен")

    @asynccontextmanager
    async def page_session(self) -> AsyncIterator[Page]:
        if self._browser is None:
            raise RuntimeError("BrowserLifecycle: вызовите start() до page_session")
        ctx_kwargs = new_context_kwargs()
        context = await self._browser.new_context(**ctx_kwargs)
        page = await context.new_page()
        page.set_default_navigation_timeout(
            settings.playwright_worker.NAVIGATION_TIMEOUT_MS
        )
        try:
            yield page
        finally:
            await context.close()
