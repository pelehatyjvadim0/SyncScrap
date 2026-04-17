import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from root.apps.workers.scheduler.logic.tick_runner import SchedulerTickRunner, _due_threshold_naive_utc


def test_due_threshold_is_naive_utc() -> None:
    with patch("root.apps.workers.scheduler.logic.tick_runner.settings") as s:
        s.scheduler.STALE_AFTER_SECONDS = 120
        t = _due_threshold_naive_utc()
        assert t.tzinfo is None


def test_run_tick_disabled_skips_work() -> None:
    async def _run() -> None:
        with patch("root.apps.workers.scheduler.logic.tick_runner.settings", new_callable=AsyncMock) as s:
            s.scheduler.ENABLED = False
            await SchedulerTickRunner().run_tick()

            s.assert_not_called()

    asyncio.run(_run())


def test_run_tick_publishes_without_mark_in_db() -> None:
    urls = ["https://a.example", "https://b.example"]
    sent = ["https://a.example", "https://b.example"]

    mock_session = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_session)
    ctx.__aexit__ = AsyncMock(return_value=None)
    sessionmaker_mock = MagicMock(return_value=ctx)

    fetch_mock = AsyncMock(return_value=urls)
    append_mock = AsyncMock(return_value=sent)

    async def _run() -> None:
        with (
            patch("root.apps.workers.scheduler.logic.tick_runner.settings") as s,
            patch(
                "root.apps.workers.scheduler.logic.tick_runner.sessionmaker",
                sessionmaker_mock,
            ),
            patch(
                "root.apps.workers.scheduler.logic.tick_runner.TargetUrlDAO.fetch_due_urls",
                fetch_mock,
            ),
            patch(
                "root.apps.workers.scheduler.logic.tick_runner.URLSpawner.append_discovery_tasks",
                append_mock,
            ),
        ):
            s.scheduler.ENABLED = True
            s.scheduler.STALE_AFTER_SECONDS = 60
            s.scheduler.MAX_URLS_PER_TICK = 500
            s.scheduler.FORCE_REFRESH = True
            s.scheduler.PUBLISH_GAP_SECONDS = 0.0
            await SchedulerTickRunner().run_tick()

    asyncio.run(_run())

    assert sessionmaker_mock.call_count == 1
    fetch_mock.assert_awaited_once()
    append_mock.assert_awaited_once()
    mock_session.commit.assert_not_awaited()
