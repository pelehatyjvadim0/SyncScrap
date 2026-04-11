import logging
from datetime import datetime, timedelta, timezone

from root.persistence.connection import sessionmaker
from root.persistence.dao.target_url import TargetUrlDAO
from root.shared.config import settings
from root.shared.url_spawner import URLSpawner

logger = logging.getLogger(__name__)


def _due_threshold_naive_utc() -> datetime:
    """Порог «старше чем» для last_scraped_at (naive UTC, как в БД)."""
    aware = datetime.now(timezone.utc) - timedelta(
        seconds=settings.scheduler.STALE_AFTER_SECONDS
    )
    return aware.replace(tzinfo=None)


class SchedulerTickRunner:
    """Один тик: выбрать цели → raw_urls → отметить last_scraped_at только для успешно отправленных."""

    async def run_tick(self) -> None:
        if not settings.scheduler.ENABLED:
            return

        threshold = _due_threshold_naive_utc()
        async with sessionmaker() as session:
            urls = await TargetUrlDAO.fetch_due_urls(
                session,
                older_than=threshold,
                limit=settings.scheduler.MAX_URLS_PER_TICK,
            )

        if not urls:
            logger.debug(
                " [⏰] Тик планировщика: целей нет (порог=%s)",
                threshold.isoformat(),
            )
            return

        logger.info(" [⏰] Тик планировщика: к отправке выбрано URL=%s", len(urls))

        sent = await URLSpawner.append_urls_in_queue(
            urls,
            force_refresh=settings.scheduler.FORCE_REFRESH,
            publish_gap_seconds=settings.scheduler.PUBLISH_GAP_SECONDS,
        )

        if not sent:
            logger.warning(" [⏰] В raw_urls ничего не ушло — last_scraped_at не обновляем")
            return

        async with sessionmaker() as session:
            try:
                await TargetUrlDAO.mark_urls_scraped(session, sent)
                await session.commit()
                logger.info(
                    " [⏰] last_scraped_at обновлён для успешно отправленных: %s",
                    len(sent),
                )
            except Exception:
                await session.rollback()
                logger.exception(
                    " [⏰] Ошибка при сохранении last_scraped_at (откат транзакции)"
                )
                raise
