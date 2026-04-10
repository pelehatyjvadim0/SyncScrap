import logging

from root.worker_parser.logic.base import BaseParser
from root.worker_parser.logic.strategies.books_toscrape import BooksToScrapeParser

logger = logging.getLogger(__name__)


def build_strategies() -> dict[str, BaseParser]:
    parser_instances: list[BaseParser] = [
        BooksToScrapeParser(),
    ]

    strategies: dict[str, BaseParser] = {}
    for parser in parser_instances:
        domain = parser.DOMAIN.strip().lower()
        if not domain:
            raise ValueError(
                f"Стратегия {parser.__class__.__name__} не указала DOMAIN"
            )
        if domain in strategies:
            raise ValueError(f"Дублирующаяся стратегия для домена {domain}")
        strategies[domain] = parser

    logger.info(" [i] Зарегистрировано стратегий парсинга: %s", len(strategies))
    return strategies
