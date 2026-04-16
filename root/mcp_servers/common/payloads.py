from typing import Any


def build_success_payload(data: dict[str, Any] | Any) -> dict[str, Any]:
    if isinstance(data, dict):
        return data
    return {"ok": True, "result": data}


def build_error_payload(
    error_code: str,
    message: str,
    details: Any = None,
    retryable: bool = False,
    trace_id: str | None = None,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": False,
        "error_code": error_code,
        "message": message,
        "details": details,
        "retryable": retryable,
    }
    if trace_id is not None:
        payload["trace_id"] = trace_id
    if idempotency_key is not None:
        payload["idempotency_key"] = idempotency_key
    return payload
