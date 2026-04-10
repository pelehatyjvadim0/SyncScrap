import logging

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class ScraperUtils:
    @staticmethod
    async def get_all_book_urls(limit: int = 100) -> list[str]:
        base_url = "https://books.toscrape.com/catalogue/page-{}.html"
        urls: list[str] = []
        page = 1

        async with httpx.AsyncClient() as client:
            while len(urls) < limit:
                response = await client.get(base_url.format(page))

                if response.status_code != 200:
                    logger.error(
                        "Failed to fetch books page %s, status=%s",
                        page,
                        response.status_code,
                    )
                    break

                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.select("h3 a")

                if not links:
                    break

                for link in links:
                    clear_url = link["href"].replace("../../../", "")
                    full_url = "https://books.toscrape.com/catalogue/" + clear_url
                    urls.append(full_url)

                    if len(urls) >= limit:
                        break

                page += 1

        return urls
