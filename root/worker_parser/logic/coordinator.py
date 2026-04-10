import logging
from urllib.parse import urlparse
from root.worker_parser.logic.base import BaseParser
from root.worker_parser.logic.schemas import BaseItemDTO
from root.worker_parser.logic.strategies.registry import build_strategies

logger = logging.getLogger(__name__)


class ParserCoordinator:
    def __init__(self, strategies: dict[str, BaseParser] | None = None):
        self._strategies = strategies or build_strategies()

    async def run_parser(self, url: str, html: str) -> list[BaseItemDTO]:
        domain = urlparse(url).netloc.replace("www.", "")

        strategy = self._strategies.get(domain)

        if not strategy:
            logger.error(" [!] Стратегия не найдена | Домен: %s | URL: %s", domain, url)
            raise ValueError(f"Нет стратегии для домена {domain}")

        logger.debug(
            " [i] Выбрана стратегия %s для домена %s",
            strategy.__class__.__name__,
            domain,
        )
        return await strategy.parse(html, url)
