from dataclasses import dataclass
from typing import Any, Callable, Awaitable

from root.shared.url_spawner import URLSpawner


@dataclass(slots=True)
class MCPTool:
    name: str
    description: str
    handler: Callable[..., Awaitable[Any]]


async def enqueue_discovery_tool(
    *,
    search_urls: list[str],
    source: str = "avito",
    city: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    sent = await URLSpawner.append_discovery_tasks(
        search_urls,
        source=source,
        city=city,
        category=category,
    )
    return {"queued": len(sent), "urls": sent}


TOOLS_REGISTRY: dict[str, MCPTool] = {
    "enqueue_discovery": MCPTool(
        name="enqueue_discovery",
        description="Put discovery URLs to broker queue",
        handler=enqueue_discovery_tool,
    ),
}
