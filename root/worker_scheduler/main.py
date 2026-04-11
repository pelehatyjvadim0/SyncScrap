import asyncio
import logging

from root.shared.config import settings
from root.shared.rabbitmq import faststream_app
from root.worker_scheduler.logic.tick_runner import SchedulerTickRunner

logger = logging.getLogger(__name__)

_scheduler_task: asyncio.Task | None = None


async def _scheduler_loop() -> None:
    runner = SchedulerTickRunner()
    interval = max(5, settings.scheduler.INTERVAL_SECONDS)
    while True:
        try:
            await runner.run_tick()
        except asyncio.CancelledError:
            logger.info(" [⏰] Цикл планировщика остановлен (cancel)")
            raise
        except Exception:
            logger.exception(
                " [⏰] Ошибка тика планировщика; следующая попытка через %ss",
                interval,
            )
        await asyncio.sleep(interval)


@faststream_app.after_startup
async def _start_scheduler_background() -> None:
    global _scheduler_task
    if not settings.scheduler.ENABLED:
        logger.info(" [⏰] Планировщик выключен (SCHEDULER_ENABLED=false)")
        return

    logger.info(
        " [⏰] Планировщик запущен: интервал=%ss max_url=%s stale=%ss force_refresh=%s",
        settings.scheduler.INTERVAL_SECONDS,
        settings.scheduler.MAX_URLS_PER_TICK,
        settings.scheduler.STALE_AFTER_SECONDS,
        settings.scheduler.FORCE_REFRESH,
    )
    _scheduler_task = asyncio.create_task(_scheduler_loop())


@faststream_app.on_shutdown
async def _stop_scheduler_background() -> None:
    global _scheduler_task
    if _scheduler_task is None or _scheduler_task.done():
        return
    _scheduler_task.cancel()
    try:
        await _scheduler_task
    except asyncio.CancelledError:
        pass
    _scheduler_task = None
    logger.info(" [⏰] Планировщик: фоновая задача завершена")
