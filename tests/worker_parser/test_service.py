import asyncio
import json

from root.worker_parser.logic.schemas import BaseItemDTO, DownloadedPageMessage
from root.worker_parser.logic.service import ParserService


class FakeMsg:
    def __init__(self, payload: dict):
        self.body = json.dumps(payload).encode()


class FakeStorage:
    async def get_html(self, key: str) -> str | None:
        if key == "ok-key":
            return "<html>ok</html>"
        return None


class FakeCoordinator:
    async def run_parser(self, url: str, html: str) -> list[BaseItemDTO]:
        return [
            BaseItemDTO(
                title="Test Book",
                price="12.34",
                currency="GBP",
                image_url="https://books.toscrape.com/image.jpg",
                url=url,
                availability=True,
            )
        ]


def test_parse_downloaded_message_from_broker_message() -> None:
    msg = FakeMsg({"storage_key": "key-1", "url": "https://books.toscrape.com/a"})
    parsed = ParserService.parse_downloaded_message(msg)

    assert isinstance(parsed, DownloadedPageMessage)
    assert parsed.storage_key == "key-1"
    assert str(parsed.url) == "https://books.toscrape.com/a"


def test_serialize_for_broker() -> None:
    result = {
        "url": "https://books.toscrape.com/a/",
        "items": [
            {
                "title": "Book",
                "price": "12.34",
                "currency": "GBP",
                "image_url": "https://books.toscrape.com/image.jpg",
                "url": "https://books.toscrape.com/catalogue/book_1/index.html",
                "availability": True,
            }
        ],
    }
    extracted = ParserService.parse_downloaded_message(
        {"storage_key": "ok-key", "url": result["url"]}
    )

    # Check serializer on real DTO model shape
    payload = ParserService.serialize_for_broker(
        asyncio.run(
            ParserService.parse_page(
                extracted,
                FakeStorage(),
                FakeCoordinator(),
            )
        )
    )
    assert payload["url"] == result["url"]
    assert len(payload["items"]) == 1
    assert payload["items"][0]["title"] == "Test Book"
