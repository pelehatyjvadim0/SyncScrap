from typing import Any, Literal, TypedDict
from urllib.parse import urlparse

from pydantic import BaseModel, Field, HttpUrl, field_validator

# Константы инструмента enqueue_discovery: лимиты, домен, таймауты.
ALLOWED_DOMAIN = "avito.ru"
PUBLISH_TIMEOUT_SECONDS = 5.0
IDEMPOTENCY_TTL_SECONDS = 300
RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_CALLS = 120


# Входной контракт MCP-инструмента: валидируем URL и пользовательские поля.
class EnqueueDiscoveryInput(BaseModel):
    search_url: HttpUrl
    source: str = Field(default="avito", max_length=32)
    city: str | None = Field(default=None, max_length=128)
    category: str | None = Field(default=None, max_length=128)
    trace_id: str | None = Field(default=None, max_length=128)
    idempotency_key: str | None = Field(default=None, max_length=256)

    @field_validator("search_url")
    @classmethod
    # Проверяем allowlist домена, чтобы tool не использовали как open relay.
    def validate_allowed_domain(cls, value: HttpUrl) -> HttpUrl:
        parsed = urlparse(str(value))
        host = (parsed.hostname or "").lower().strip(".")
        is_allowed = host == ALLOWED_DOMAIN or host.endswith(f".{ALLOWED_DOMAIN}")
        if not is_allowed:
            raise ValueError(f"домен search_url должен быть {ALLOWED_DOMAIN} или его поддоменом")
        return value


# Формат ответа при ошибке - единый для всех веток инструмента.
class ErrorResponse(TypedDict):
    ok: Literal[False]
    error_code: str
    message: str
    details: Any
    trace_id: str
    idempotency_key: str | None
    retryable: bool


# Формат успешного ответа - queued или duplicate_ignored.
class SuccessResponse(TypedDict):
    ok: Literal[True]
    status: Literal["queued", "duplicate_ignored"]
    queue_name: str
    trace_id: str
    idempotency_key: str
    task: dict[str, Any]
