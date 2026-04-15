# Тот же формат тела, что и у RAW_URLS (JSON RawUrlMessage или одна строка URL).

from root.worker_downloader.logic.message_payload import (
    RawUrlPayloadError,
    decode_raw_bytes,
    parse_raw_url_message,
)

__all__ = [
    "RawUrlPayloadError",
    "decode_raw_bytes",
    "parse_raw_url_message",
]
