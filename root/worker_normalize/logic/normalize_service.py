import re
from decimal import Decimal

from root.shared.schemas.canonical_listing import CanonicalListing
from root.shared.schemas.discovered_listing import DiscoveredListing

_TAG_RE = re.compile(r"<[^>]+>")
_WS_RE = re.compile(r"\s+")
_SCAM_PATTERNS = [
    re.compile(r"telegram|тг|whatsapp", re.IGNORECASE),
    re.compile(r"предоплат", re.IGNORECASE),
    re.compile(r"внесите.*залог", re.IGNORECASE),
]


class NormalizeService:
    @staticmethod
    def html_to_markdown(html: str) -> str:
        no_tags = _TAG_RE.sub(" ", html)
        cleaned = _WS_RE.sub(" ", no_tags).strip()
        return cleaned[:4000]

    @staticmethod
    def scam_score(text: str) -> float:
        hits = sum(1 for pattern in _SCAM_PATTERNS if pattern.search(text))
        return min(1.0, hits / len(_SCAM_PATTERNS))

    @classmethod
    def to_canonical(
        cls,
        *,
        listing: DiscoveredListing,
        html: str,
        version: int,
        currency: str = "RUB",
    ) -> CanonicalListing:
        markdown = cls.html_to_markdown(html)
        title = listing.title_short or f"{listing.source}:{listing.listing_id}"
        price = listing.price if isinstance(listing.price, Decimal) else listing.price
        return CanonicalListing(
            source=listing.source,
            listing_id=listing.listing_id,
            idempotency_key=listing.idempotency_key,
            version=version,
            url=listing.url,
            title=title,
            description_markdown=markdown,
            price=price,
            currency=currency,
            city=listing.city,
            scam_score=cls.scam_score(markdown),
            attributes={"content_hash_light": listing.content_hash_light},
        )
