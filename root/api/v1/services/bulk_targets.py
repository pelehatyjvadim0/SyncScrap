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


class BulkTargetsService:
    @staticmethod
    async def add_urls(session: AsyncSession, urls: list[str]) -> BulkTargetsResponse:
        total = len(urls)
        if total == 0:
            return BulkTargetsResponse(total=0, inserted=0, duplicates=0)

        normalized: list[str] = []
        for url in urls:
            try:
                RawUrlMessage(url=HttpUrl(url), force_refresh=False)
            except ValidationError as exc:
                raise InvalidTargetUrlError(url) from exc
            normalized.append(str(HttpUrl(url)))

        seen: set[str] = set()
        unique_urls: list[str] = []
        duplicate_in_request = 0
        for u in normalized:
            if u in seen:
                duplicate_in_request += 1
                continue
            seen.add(u)
            unique_urls.append(u)

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
