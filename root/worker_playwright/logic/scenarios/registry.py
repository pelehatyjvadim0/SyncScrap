from root.shared.net.hostname import get_hostname
from root.worker_playwright.logic.scenarios.avito import AvitoScenario
from root.worker_playwright.logic.scenarios.base import SiteScenario
from root.worker_playwright.logic.scenarios.default import DefaultScenario


def scenario_for_url(url: str) -> SiteScenario:
    host = get_hostname(url)
    if host == "avito.ru":
        return AvitoScenario()
    return DefaultScenario()
