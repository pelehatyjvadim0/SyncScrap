from abc import ABC, abstractmethod

from root.contracts.v1.discovered_listing import DiscoveredListing


class BaseScoutStrategy(ABC):
    DOMAIN: str = ""

    @abstractmethod
    def parse(
        self,
        *,
        html: str,
        source: str,
        base_url: str,
        city: str | None,
    ) -> list[DiscoveredListing]:
        raise NotImplementedError
