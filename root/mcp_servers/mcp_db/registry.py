from root.mcp_servers.common.registry import MCPTool
from root.mcp_servers.mcp_db.tools.hybrid_search_candidates import (
    HybridSearchCandidatesInput,
    hybrid_search_candidates_tool,
)
from root.mcp_servers.mcp_db.tools.list_listings import ListListingsInput, list_listings_tool

TOOLS_REGISTRY: dict[str, MCPTool] = {
    "hybrid_search_candidates": MCPTool(
        name="hybrid_search_candidates",
        description="Гибридный поиск кандидатов (SQL + Qdrant + rerank), как в API hybrid search",
        input_model=HybridSearchCandidatesInput,
        handler=hybrid_search_candidates_tool,
    ),
    "list_listings": MCPTool(
        name="list_listings",
        description="Список записей listing_versions с пагинацией и фильтром по городу (read-only)",
        input_model=ListListingsInput,
        handler=list_listings_tool,
    ),
}
