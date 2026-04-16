from collections.abc import Callable

from pydantic import BaseModel


class MCPTool:
    def __init__(self, name: str, description: str, input_model: type[BaseModel], handler: Callable):
        self.name = name
        self.description = description
        self.input_model = input_model
        self.handler = handler
