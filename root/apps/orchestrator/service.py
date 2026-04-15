from pydantic import BaseModel, Field

from root.apps.orchestrator.mcp_tools import TOOLS_REGISTRY


class UserIntent(BaseModel):
    source: str = Field(default="avito")
    city: str | None = None
    category: str | None = None
    search_urls: list[str] = Field(default_factory=list)


class LLMOrchestrator:
    async def dispatch(self, intent: UserIntent) -> dict:
        tool = TOOLS_REGISTRY["enqueue_discovery"]
        payload = await tool.handler(
            search_urls=intent.search_urls,
            source=intent.source,
            city=intent.city,
            category=intent.category,
        )
        return {"tool": tool.name, "result": payload}
