import logging
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from root.persistence.relational_store.models.target import TargetUrl

logger = logging.getLogger(__name__)

_MARK_CHUNK_SIZE = 500


class TargetUrlDAO:
    @staticmethod
    async def bulk_insert_new_urls(session: AsyncSession, urls: Sequence[str]) -> int:
        """
        Вставка только новых URL (`ON CONFLICT DO NOTHING` по `url`).
        `urls` без повторов. Возвращает число реально вставленных строк.
        """
        if not urls:
            return 0
        stmt = (
            insert(TargetUrl)
            .values(
                [
                    {"url": u, "last_scraped_at": None, "is_active": True}
                    for u in urls
                ]
            )
            .on_conflict_do_nothing(index_elements=["url"])
            .returning(TargetUrl.id)
        )
        result = await session.execute(stmt)
        return len(result.scalars().all())

    @staticmethod
    async def fetch_due_urls(
        session: AsyncSession,
        *, # первый аргумент до звёздочки - позиционный, после звёздочки - все именованные, тут это контракт на именованные аргументы!!!!!!
        older_than: datetime,
        limit: int,
    ) -> list[str]:
        """
        Активные URL, у которых ещё не было скрапа или last_scraped_at старше порога.
        `older_than` — naive UTC (как в колонке БД).
        """
        stmt = (
            select(TargetUrl.url)
            .where(TargetUrl.is_active.is_(True))
            .where(
                or_(
                    TargetUrl.last_scraped_at.is_(None),
                    TargetUrl.last_scraped_at < older_than,
                )
            )
            .order_by(TargetUrl.id.asc())
            .limit(limit)
        )
        logger.info(
            " [DB] Выборка целей: older_than=%s (UTC naive), лимит=%s",
            older_than.isoformat(),
            limit,
        )
        result = await session.execute(stmt)
        urls = list(result.scalars().all())
        logger.info(" [DB] Найдено целей к отправке в очередь: %s", len(urls))
        return urls

    @staticmethod
    async def mark_urls_scraped(session: AsyncSession, urls: Sequence[str]) -> int:
        """Пакетно обновляет last_scraped_at. Возвращает число обработанных URL."""
        if not urls:
            logger.debug(" [DB] Обновление last_scraped_at: список пуст, пропуск")
            return 0

        now = datetime.now(timezone.utc).replace(tzinfo=None)
        url_list = list(urls)

        for offset in range(0, len(url_list), _MARK_CHUNK_SIZE):
            chunk = url_list[offset : offset + _MARK_CHUNK_SIZE]
            stmt = (
                update(TargetUrl)
                .where(TargetUrl.url.in_(chunk))
                .values(last_scraped_at=now)
            )
            await session.execute(stmt)
            logger.debug(
                " [DB] Пакет last_scraped_at: смещение=%s, размер=%s",
                offset,
                len(chunk),
            )

        logger.info(" [DB] Обновлено last_scraped_at для URL: %s", len(url_list))
        return len(url_list)
