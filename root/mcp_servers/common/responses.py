import json
from typing import Any

import mcp.types as types

from root.mcp_servers.common.payloads import build_error_payload, build_success_payload


def to_text_content(payload: dict[str, Any] | Any) -> list[types.TextContent]:
    body = payload if isinstance(payload, dict) else build_success_payload(payload)
    return [
        types.TextContent(
            type="text",
            text=json.dumps(body, ensure_ascii=False, indent=2),
        )
    ]


def success_response(payload: dict[str, Any] | Any) -> list[types.TextContent]:
    return to_text_content(build_success_payload(payload))


def error_response(
    error_code: str,
    message: str,
    details: Any = None,
    retryable: bool = False,
) -> list[types.TextContent]:
    return to_text_content(
        build_error_payload(
            error_code=error_code,
            message=message,
            details=details,
            retryable=retryable,
        )
    )
