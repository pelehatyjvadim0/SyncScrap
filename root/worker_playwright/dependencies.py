from root.shared.redis_client import RedisManager
from root.worker_playwright.logic.browser.lifecycle import BrowserLifecycle


class PlaywrightWorkerResources:
    """Redis + пул браузера для воркера Playwright."""

    def __init__(self) -> None:
        self.storage: RedisManager | None = None
        self.browser: BrowserLifecycle | None = None

    async def init_all(self) -> None:
        if self.storage is None:
            self.storage = RedisManager()
            await self.storage.connect()
        if self.browser is None:
            self.browser = BrowserLifecycle()
            await self.browser.start()

    async def close_all(self) -> None:
        if self.browser is not None:
            await self.browser.stop()
            self.browser = None
        if self.storage is not None:
            await self.storage.close()
            self.storage = None

    async def get_storage(self) -> RedisManager:
        if self.storage is None:
            await self.init_all()
        assert self.storage is not None
        return self.storage

    async def get_browser(self) -> BrowserLifecycle:
        if self.browser is None:
            await self.init_all()
        assert self.browser is not None
        return self.browser


pw_res = PlaywrightWorkerResources()
