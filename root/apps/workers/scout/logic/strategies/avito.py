import logging
import re
from decimal import Decimal
from urllib.parse import urljoin

from pydantic import HttpUrl, TypeAdapter

from root.contracts.v1.discovered_listing import DiscoveredListing
from root.apps.workers.scout.logic.strategies.base import BaseScoutStrategy

logger = logging.getLogger(__name__)

_AVITO_ITEM_RE = re.compile(r"/([a-z0-9_]+)_(\d+)$", re.IGNORECASE)
_PRICE_RE = re.compile(r"(\d[\d\s]{2,})")
_HTTP_URL_ADAPTER = TypeAdapter(HttpUrl)


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


class AvitoScoutStrategy(BaseScoutStrategy):
    DOMAIN = "avito.ru"

    def parse(
        self,
        *,
        html: str,
        source: str,
        base_url: str,
        city: str | None,
    ) -> list[DiscoveredListing]:
        from selectolax.lexbor import LexborHTMLParser

        tree = LexborHTMLParser(html)
        results: list[DiscoveredListing] = []

        for anchor in tree.css("a[href]"):
            href = anchor.attributes.get("href") or ""
            if "/item/" not in href and "_" not in href:
                continue
            abs_url = urljoin(base_url, href)
            match = _AVITO_ITEM_RE.search(abs_url.split("?")[0].rstrip("/"))
            if not match:
                continue

            listing_id = match.group(2)
            title = (
                anchor.attributes.get("title")
                or anchor.text(separator=" ", strip=True)
                or ""
            ).strip()
            container_text = (
                anchor.parent.text(separator=" ", strip=True)
                if anchor.parent is not None
                else ""
            )
            price = _parse_price(container_text)

            try:
                parsed_url = _HTTP_URL_ADAPTER.validate_python(abs_url)
                results.append(
                    DiscoveredListing(
                        source=source,
                        listing_id=listing_id,
                        url=parsed_url,
                        price=price,
                        title_short=title or None,
                        city=city,
                    )
                )
            except Exception as exc:
                logger.debug(" [Scout] Skip broken listing %s: %s", abs_url, exc)
                continue
        return results
