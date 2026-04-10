from decimal import Decimal, InvalidOperation
import re
from urllib.parse import urljoin
import logging
from root.worker_parser.logic.schemas import StorageProtocol

logger = logging.getLogger(__name__)


class ParserUtils:
    @staticmethod
    def clean_price(raw_price: str) -> Decimal:
        if not raw_price:
            return Decimal("0")

        cleaned = re.sub(r"[^0-9.,]", "", raw_price)

        if "," in cleaned and "." in cleaned:
            cleaned = cleaned.replace(",", "")

        cleaned = cleaned.replace(",", ".")

        try:
            return Decimal(cleaned)
        except (InvalidOperation, ValueError):
            return Decimal("0")

    @staticmethod
    def url_join(current_page_url: str, relative_path: str) -> str:
        return urljoin(current_page_url, relative_path)

    @staticmethod
    async def storage_get_html(storage: StorageProtocol, key: str) -> str:
        html = await storage.get_html(key)
        if html is None:
            logger.critical(" [!] Не удалось получить HTML по ключу %s", key)
            raise ValueError(f"Не удалось получить HTML по ключу {key}")
        return html
