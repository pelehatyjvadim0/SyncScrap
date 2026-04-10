import logging
from selectolax.lexbor import LexborHTMLParser
from root.worker_parser.utils import ParserUtils
from root.worker_parser.logic.base import BaseParser
from root.worker_parser.logic.schemas import BaseItemDTO

logger = logging.getLogger(__name__)


class BooksToScrapeParser(BaseParser):
    DOMAIN = "books.toscrape.com"

    def __init__(self):
        self._currency_map = {"£": "GBP"}

    def _extract_title(self, link_node) -> str:
        if not link_node:
            return "Unknown"
        return link_node.attributes.get("title", "Unknown")

    def _extract_price_and_currency(self, price_node) -> tuple:
        price_raw = price_node.text(strip=True) if price_node else "0"
        price_decimal = ParserUtils.clean_price(price_raw)
        currency = self._currency_map.get(price_raw[:1], "UNKNOWN")
        return price_decimal, currency

    def _extract_image_url(self, img_node, page_url: str):
        if not img_node:
            return None
        image_rel_url = img_node.attributes.get("src")
        if not image_rel_url:
            return None
        return ParserUtils.url_join(page_url, image_rel_url)

    def _extract_product_url(self, link_node, page_url: str) -> str:
        if not link_node:
            return page_url
        product_rel_url = link_node.attributes.get("href")
        if not product_rel_url:
            return page_url
        return ParserUtils.url_join(page_url, product_rel_url)

    def _extract_availability(self, avail_node) -> bool:
        if not avail_node:
            return False
        return "in stock" in avail_node.text().lower()

    async def parse(self, html: str, url: str) -> list[BaseItemDTO]:
        tree = LexborHTMLParser(html)
        items = tree.css(".product_pod")

        if not items:
            logger.warning(
                "🔎 На странице не найдено товаров (.product_pod) | URL: %s", url
            )
            return []

        result: list[BaseItemDTO] = []

        for index, item in enumerate(items, 1):
            try:
                link_node = item.css_first("h3 a")
                price_node = item.css_first(".price_color")
                img_node = item.css_first("div.image_container img")
                avail_node = item.css_first("p.instock.availability")

                title = self._extract_title(link_node)
                price_decimal, currency = self._extract_price_and_currency(price_node)
                full_image_url = self._extract_image_url(img_node, url)
                product_url = self._extract_product_url(link_node, url)
                is_available = self._extract_availability(avail_node)

                dto = BaseItemDTO(
                    title=title,
                    price=price_decimal,
                    currency=currency,
                    image_url=full_image_url,
                    url=product_url,
                    availability=is_available,
                )
                result.append(dto)

            except Exception as e:
                logger.error("✖️  Ошибка парсинга элемента #%d на %s: %s", index, url, e)
                continue

        logger.debug(
            "📊 Страница обработана: %d/%d товаров успешно", len(result), len(items)
        )
        return result
