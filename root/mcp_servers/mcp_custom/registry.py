from root.mcp_servers.mcp_custom.tools.enqueue_discovery.schemas import EnqueueDiscoveryInput
from root.mcp_servers.mcp_custom.tools.enqueue_discovery import enqueue_discovery_tool
from pydantic import BaseModel
from typing import Callable

class MCPTool:
    def __init__(self, name: str, description: str, input_model: type[BaseModel], handler: Callable):
        self.name = name
        self.description = description
        self.input_model = input_model
        self.handler = handler

TOOLS_REGISTRY: dict[str, MCPTool] = {
    "enqueue_discovery": MCPTool(
        name="enqueue_discovery",
        description="Постановка discovery задач в очередь",
        input_model=EnqueueDiscoveryInput,
        handler=enqueue_discovery_tool,
    ),
}