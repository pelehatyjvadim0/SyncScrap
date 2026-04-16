from root.mcp_servers.common.registry import MCPTool
from root.mcp_servers.mcp_custom.tools.enqueue_discovery import enqueue_discovery_tool
from root.mcp_servers.mcp_custom.tools.enqueue_discovery.schemas import EnqueueDiscoveryInput

TOOLS_REGISTRY: dict[str, MCPTool] = {
    "enqueue_discovery": MCPTool(
        name="enqueue_discovery",
        description="Постановка discovery задач в очередь",
        input_model=EnqueueDiscoveryInput,
        handler=enqueue_discovery_tool,
    ),
}
