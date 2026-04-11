import asyncio

from root.worker_parser.logic.base import BaseParser
from root.worker_parser.logic.coordinator import ParserCoordinator
from root.worker_parser.logic.schemas import BaseItemDTO


class FakeParser(BaseParser):
    DOMAIN = "example.com"

    async def parse(self, html: str, url: str) -> list[BaseItemDTO]:
        return [
            BaseItemDTO(
                title="Parsed",
                price="1.00",
                currency="USD",
                image_url=None,
                url=url,
                availability=True,
            )
        ]


def test_coordinator_uses_domain_strategy() -> None:
    coordinator = ParserCoordinator(strategies={"example.com": FakeParser()})
    result = asyncio.run(
        coordinator.run_parser("https://www.example.com/items/1", "<html></html>")
    )
    assert len(result) == 1
    assert result[0].title == "Parsed"


def test_coordinator_raises_for_unknown_domain() -> None:
    coordinator = ParserCoordinator(strategies={"example.com": FakeParser()})
    try:
        asyncio.run(coordinator.run_parser("https://unknown-domain.com", "<html></html>"))
        assert False, "Ожидали ValueError для неизвестного домена"
    except ValueError as exc:
        assert "Нет стратегии для домена" in str(exc)
