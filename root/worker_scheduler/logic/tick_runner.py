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
    """Один тик: выбрать цели → публикация в raw_urls. last_scraped_at ставит worker_db после записи книг."""

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
            logger.info(
                " [⏰] Целей к отправке нет. Порог last_scraped_at < %s (UTC naive). ",
                threshold.isoformat(),
            )
            return

        logger.info(" [⏰] Тик планировщика: к отправке выбрано URL=%s", len(urls))

        sent = await URLSpawner.append_discovery_tasks(
            urls,
            source="avito",
        )

        if not sent:
            logger.warning(" [⏰] В discovery_urls ничего не ушло")
            return

        logger.info(" [⏰] Опубликовано в discovery_urls: %s", len(sent))
