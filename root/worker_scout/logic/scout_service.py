import logging
import re
from decimal import Decimal
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from root.shared.schemas.discovered_listing import DiscoveredListing

logger = logging.getLogger(__name__)

_AVITO_ITEM_RE = re.compile(r"/([a-z0-9_]+)_(\d+)$", re.IGNORECASE)
_PRICE_RE = re.compile(r"(\d[\d\s]{2,})")


def _parse_price(raw_text: str | None) -> Decimal | None:
    if not raw_text:
        return None
    match = _PRICE_RE.search(raw_text.replace("\xa0", " "))
    if not match:
        return None
    normalized = match.group(1).replace(" ", "")
    try:
        return Decimal(normalized)
    except Exception:
        return None


class ScoutService:
    @staticmethod
    def parse_discovery_page(
        *,
        html: str,
        source: str,
        base_url: str,
        city: str | None,
    ) -> list[DiscoveredListing]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[DiscoveredListing] = []

        for anchor in soup.select("a[href]"):
            href = anchor.get("href") or ""
            if "/item/" not in href and "_" not in href:
                continue
            abs_url = urljoin(base_url, href)
            match = _AVITO_ITEM_RE.search(abs_url.split("?")[0].rstrip("/"))
            if not match:
                continue

            listing_id = match.group(2)
            title = (anchor.get("title") or anchor.get_text(" ", strip=True) or "").strip()
            container_text = anchor.parent.get_text(" ", strip=True) if anchor.parent else ""
            price = _parse_price(container_text)

            try:
                results.append(
                    DiscoveredListing(
                        source=source,
                        listing_id=listing_id,
                        url=abs_url,
                        price=price,
                        title_short=title or None,
                        city=city,
                    )
                )
            except Exception as exc:
                logger.debug(" [Scout] Skip broken listing %s: %s", abs_url, exc)
                continue
        return results
