import json
import logging
from typing import Any

from root.shared.schemas.raw_url_message import RawUrlMessage

logger = logging.getLogger(__name__)


class RawUrlPayloadError(ValueError):
    """Невалидное или пустое тело сообщения RAW_URLS."""


def decode_raw_bytes(msg: Any) -> str:
    """Достаёт тело сообщения FastStream / брокера как строку UTF-8."""
    if hasattr(msg, "body"):
        raw = msg.body
        if isinstance(raw, bytes):
            return raw.decode()
        if isinstance(raw, str):
            return raw
        return str(raw)
    if isinstance(msg, bytes):
        return msg.decode()
    if isinstance(msg, str):
        return msg
    return str(msg)


def parse_raw_url_message(raw: str) -> RawUrlMessage:
    """
    Поддерживает JSON (`RawUrlMessage`) и обратную совместимость: одна строка = URL.
    """
    text = raw.strip()
    if not text:
        raise RawUrlPayloadError("Пустое тело сообщения RAW_URLS")

    if text.startswith("{"):
        try:
            data = json.loads(text)
        except json.JSONDecodeError as exc:
            logger.warning(" [↓] JSON в RAW_URLS не разобран: %s", exc)
            raise RawUrlPayloadError(f"Невалидный JSON: {exc}") from exc
        return RawUrlMessage.model_validate(data)

    return RawUrlMessage.model_validate({"url": text})
