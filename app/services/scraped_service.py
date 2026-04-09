from bs4 import BeautifulSoup
import logging
import re

logger = logging.getLogger(__name__)


class ScrapedService:
    CURRENCY_MAP = {"£": "GBP", "$": "USD", "€": "EUR"}

    @classmethod
    async def scrap_book_html(cls, html: str):
        book_title = None
        book_price = None

        soup = BeautifulSoup(html)
        scrap_book_conf = {
            "title": "div.col-sm-6.product_main h1",
            "price": "div.col-sm-6.product_main p.price_color",
        }

        tag_title = soup.select_one(scrap_book_conf["title"])
        logger.info(f" [*] Тег title получен -> {tag_title}")
        book_title = tag_title.text if tag_title else None
        tag_price = soup.select_one(scrap_book_conf["price"])

        book_price = tag_price.text if tag_price else None

        currency_symbol = re.sub(r"[0-9.,\s]", "", str(book_price))
        clear_book_price = re.sub(r"[^\d.]", "", str(book_price))

        currency_code = cls.CURRENCY_MAP.get(currency_symbol, "UNKNOWN")

        if book_title and book_price:
            scraped_data = {
                "title": book_title,
                "price": clear_book_price,
                "currency": currency_code,
            }
            return scraped_data
        else:
            return None
