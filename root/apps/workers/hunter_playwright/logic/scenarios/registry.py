from root.shared.net.hostname import get_hostname
from root.apps.workers.hunter_playwright.logic.scenarios.avito import AvitoScenario
from root.apps.workers.hunter_playwright.logic.scenarios.base import SiteScenario
from root.apps.workers.hunter_playwright.logic.scenarios.default import DefaultScenario

_SCENARIOS_BY_DOMAIN: dict[str, SiteScenario] = {
    AvitoScenario.DOMAIN: AvitoScenario(),
}
_DEFAULT_SCENARIO = DefaultScenario()


def register_scenario(scenario: SiteScenario) -> None:
    domain = scenario.DOMAIN.strip().lower()
    if not domain or domain == "*":
        raise ValueError("Scenario DOMAIN must be a concrete hostname")
    _SCENARIOS_BY_DOMAIN[domain] = scenario


def scenario_for_url(url: str) -> SiteScenario:
    host = get_hostname(url)
    if host is None:
        return _DEFAULT_SCENARIO
    return _SCENARIOS_BY_DOMAIN.get(host, _DEFAULT_SCENARIO)
