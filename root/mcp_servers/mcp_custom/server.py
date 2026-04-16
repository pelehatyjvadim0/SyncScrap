import asyncio
import logging

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from pydantic import ValidationError

from root.mcp_servers.common.errors import EXECUTION_FAILED, INVALID_PARAMS, TOOL_NOT_FOUND
from root.mcp_servers.common.payloads import build_error_payload, build_success_payload
from root.mcp_servers.common.responses import to_text_content
from root.mcp_servers.mcp_custom.registry import MCPTool, TOOLS_REGISTRY
from root.shared.rabbitmq import broker
from root.shared.redis_client import redis_manager

logger = logging.getLogger(__name__)


class MCPCustomApp:
    def __init__(self):
        self.server = Server("mcp-custom-server")
        self.registry = TOOLS_REGISTRY
        self._setup_handlers()

    def _setup_handlers(self):
        self.server.list_tools()(self.handle_list_tools)
        self.server.call_tool()(self.handle_call_tool)

    async def handle_list_tools(self):
        return [
            types.Tool(
                name=t.name,
                description=t.description,
                inputSchema=t.input_model.model_json_schema(),
            )
            for t in self.registry.values()
        ]

    async def handle_call_tool(self, name: str, arguments: dict | None):
        tool = self.registry.get(name)
        if not tool:
            return to_text_content(build_error_payload(TOOL_NOT_FOUND, f"Unknown tool: {name}"))

        arguments_obj = {} if arguments is None else arguments
        if not isinstance(arguments_obj, dict):
            return to_text_content(
                build_error_payload(
                    INVALID_PARAMS,
                    "Аргументы должны быть словарем",
                    details="Arguments must be a dictionary",
                )
            )

        try:
            validated_args = tool.input_model.model_validate(arguments_obj)
        except ValidationError as exc:
            return to_text_content(build_error_payload(INVALID_PARAMS, str(exc), details=exc.errors()))

        try:
            result = await tool.handler(**validated_args.model_dump())
            return to_text_content(build_success_payload(result))
        except Exception as e:
            return to_text_content(build_error_payload(EXECUTION_FAILED, str(e), retryable=False))

    async def run(self):
        logger.info(" [🚀] Установка соединения с Redis...")
        await redis_manager.connect()
        logger.info(" [✅] Соединение с Redis установлено")

        logger.info(" [🚀] Установка соединения с RabbitMQ...")
        await broker.connect()
        logger.info(" [✅] Соединение с RabbitMQ установлено")

        try:
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="mcp_custom_server",
                        server_version="0.1.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        ),
                    ),
                )
        finally:
            logger.info(" [🏁] Завершение работы MCP Custom Server | Соединение с RabbitMQ и Redis закрыто")
            await broker.close()
            await redis_manager.close()


if __name__ == "__main__":
    app = MCPCustomApp()
    asyncio.run(app.run())
