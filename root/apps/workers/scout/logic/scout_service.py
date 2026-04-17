from root.contracts.v1.discovered_listing import DiscoveredListing
from root.apps.workers.scout.logic.strategies.registry import default_scout_strategy_registry


class ScoutService:
    @staticmethod
    def parse_discovery_page(
        *,
        html: str,
        source: str,
        base_url: str,
        city: str | None,
    ) -> list[DiscoveredListing]:
        strategy = default_scout_strategy_registry.resolve(base_url)
        return strategy.parse(
            html=html,
            source=source,
            base_url=base_url,
            city=city,
        )
