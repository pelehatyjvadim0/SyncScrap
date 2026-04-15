# Параметры BrowserContext (viewport, locale, proxy - доработать по мере необходимости)

from root.shared.config import settings


def new_context_kwargs() -> dict:
    pw = settings.playwright_worker
    return {
        "viewport": {
            "width": pw.VIEWPORT_WIDTH,
            "height": pw.VIEWPORT_HEIGHT,
        },
        "locale": "ru-RU",
        "timezone_id": "Europe/Moscow",
    }
