import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


def test_mcp_db_list_tools_smoke() -> None:
    from root.mcp_servers.mcp_db.server import MCPDatabaseApp

    app = MCPDatabaseApp()
    tools = asyncio.run(app.handle_list_tools())
    names = {t.name for t in tools}
    assert "hybrid_search_candidates" in names
    assert "list_listings" in names


def test_list_listings_tool_mock_session() -> None:
    from root.mcp_servers.mcp_db.tools.list_listings import list_listings_tool

    mock_row = MagicMock()
    mock_row.idempotency_key = "k1"
    mock_row.version = 1
    mock_row.title = "t"
    mock_row.price = None
    mock_row.currency = "RUB"
    mock_row.city = "msk"
    mock_row.attributes = {}
    mock_row.content_hash = "h"
    mock_row.created_at = None

    scalar_result = MagicMock()
    scalar_result.all = MagicMock(return_value=[mock_row])
    exec_result = MagicMock()
    exec_result.scalars = MagicMock(return_value=scalar_result)

    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=exec_result)

    class _FakeSessionCtx:
        def __init__(self, session: AsyncMock) -> None:
            self._session = session

        async def __aenter__(self) -> AsyncMock:
            return self._session

        async def __aexit__(self, *args: object) -> None:
            return None

    def _fake_sessionmaker():
        return _FakeSessionCtx(mock_session)

    async def _run() -> dict:
        with patch("root.mcp_servers.mcp_db.tools.list_listings.sessionmaker", _fake_sessionmaker):
            return await list_listings_tool(city=None, limit=5, offset=0)

    out = asyncio.run(_run())
    assert out["ok"] is True
    assert out["count"] == 1
    assert out["items"][0]["listing_id"] == "k1"
