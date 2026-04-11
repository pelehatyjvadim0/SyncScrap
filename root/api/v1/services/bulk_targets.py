from pydantic import HttpUrl, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from root.api.v1.schemas.bulk_targets import BulkTargetsResponse
from root.persistence.dao.target_url import TargetUrlDAO
from root.shared.schemas.raw_url_message import RawUrlMessage


class InvalidTargetUrlError(Exception):
    """Невалидная строка URL при массовом добавлении целей."""

    def __init__(self, url: str) -> None:
        self.url = url
        super().__init__(f"Невалидный URL: {url}")


def _normalize_urls(urls: list[str]) -> list[str]:
    """Валидация и каноническая строка HttpUrl; длина совпадает с len(urls)."""
    out: list[str] = []
    for url in urls:
        try:
            RawUrlMessage(url=HttpUrl(url), force_refresh=False)
        except ValidationError as exc:
            raise InvalidTargetUrlError(url) from exc
        out.append(str(HttpUrl(url)))
    return out


def _unique_in_order(urls: list[str]) -> tuple[list[str], int]:
    """
    Уникальные URL в порядке первого вхождения.
    Второе значение — сколько позиций в исходном списке были повторами уже виденного URL.
    """
    if not urls:
        return [], 0
    unique = list(dict.fromkeys(urls)) # убираем повторяющиеся urls {'unqie_url': None...} затем приводим к list и сохраняем порядок и уникальность
    duplicate_in_request = len(urls) - len(unique)
    return unique, duplicate_in_request


class BulkTargetsService:
    @staticmethod
    async def add_urls(session: AsyncSession, urls: list[str]) -> BulkTargetsResponse:
        total = len(urls)
        if total == 0:
            return BulkTargetsResponse(total=0, inserted=0, duplicates=0)

        normalized = _normalize_urls(urls)
        unique_urls, duplicate_in_request = _unique_in_order(normalized)

        if not unique_urls:
            return BulkTargetsResponse(total=total, inserted=0, duplicates=total)

        inserted = await TargetUrlDAO.bulk_insert_new_urls(session, unique_urls)
        await session.commit()

        skipped_in_db = len(unique_urls) - inserted
        duplicates = duplicate_in_request + skipped_in_db

        return BulkTargetsResponse(
            total=total,
            inserted=inserted,
            duplicates=duplicates,
        )
