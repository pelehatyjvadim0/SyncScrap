import json

import pytest
from pydantic import ValidationError

from root.worker_downloader.logic.message_payload import (
    RawUrlPayloadError,
    decode_raw_bytes,
    parse_raw_url_message,
)


class _Msg:
    def __init__(self, body: bytes):
        self.body = body


def test_decode_raw_bytes_from_msg() -> None:
    raw = decode_raw_bytes(_Msg(b"https://example.com/path"))
    assert raw == "https://example.com/path"


def test_parse_plain_string_url() -> None:
    m = parse_raw_url_message("  https://books.toscrape.com/catalogue/page-1.html  ")
    assert str(m.url).startswith("https://books.toscrape.com/")
    assert m.force_refresh is False


def test_parse_json_full_message() -> None:
    payload = {"url": "https://example.com/a", "force_refresh": True}
    m = parse_raw_url_message(json.dumps(payload))
    assert str(m.url) == "https://example.com/a"
    assert m.force_refresh is True


def test_parse_empty_raises() -> None:
    with pytest.raises(RawUrlPayloadError):
        parse_raw_url_message("   ")


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(RawUrlPayloadError):
        parse_raw_url_message("{not json")


def test_parse_invalid_url_raises() -> None:
    with pytest.raises(ValidationError):
        parse_raw_url_message("not-a-url")
