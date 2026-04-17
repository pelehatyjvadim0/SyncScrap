from root.contracts.v1.discovered_listing import DiscoveredListing
from root.apps.workers.scout.logic.strategies.base import BaseScoutStrategy


class DefaultScoutStrategy(BaseScoutStrategy):
    """Безопасный fallback: неизвестный домен не парсим эвристиками."""

    DOMAIN = "*"

    def parse(
        self,
        *,
        html: str,
        source: str,
        base_url: str,
        city: str | None,
    ) -> list[DiscoveredListing]:
        return []
