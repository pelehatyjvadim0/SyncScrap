import logging

from root.shared.net.hostname import get_hostname
from root.apps.workers.scout.logic.strategies.avito import AvitoScoutStrategy
from root.apps.workers.scout.logic.strategies.base import BaseScoutStrategy
from root.apps.workers.scout.logic.strategies.default import DefaultScoutStrategy

logger = logging.getLogger(__name__)


class ScoutStrategyRegistry:
    def __init__(self) -> None:
        self._by_domain: dict[str, BaseScoutStrategy] = {}
        self._default = DefaultScoutStrategy()

    def register(self, strategy: BaseScoutStrategy) -> None:
        domain = strategy.DOMAIN.strip().lower()
        if not domain or domain == "*":
            raise ValueError("Strategy DOMAIN must be a concrete hostname")
        self._by_domain[domain] = strategy

    def resolve(self, url: str) -> BaseScoutStrategy:
        host = get_hostname(url)
        if host is None:
            return self._default
        return self._by_domain.get(host, self._default)


default_scout_strategy_registry = ScoutStrategyRegistry()
default_scout_strategy_registry.register(AvitoScoutStrategy())

logger.debug(
    " [Scout] registered discovery strategies: %s",
    sorted(default_scout_strategy_registry._by_domain),
)
