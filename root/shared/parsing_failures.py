from __future__ import annotations

from dataclasses import dataclass

_CAPTCHA_MARKERS = (
    "captcha",
    "are you human",
    "access denied",
    "robot",
    "challenge",
)


@dataclass(slots=True)
class ParsingFailure(Exception):
    reason: str
    details: str | None = None

    def __str__(self) -> str:
        if self.details:
            return f"{self.reason}: {self.details}"
        return self.reason


def detect_html_block_reason(html: str | None) -> str | None:
    if not html:
        return None

    lowered = html.lower()
    for marker in _CAPTCHA_MARKERS:
        if marker in lowered:
            return "captcha_detected"
    return None


def compose_reason(base: str, detail: str | None = None) -> str:
    return f"{base}:{detail}" if detail else base


def resolve_failure_reason(
    *,
    fallback: str,
    html: str | None = None,
    exc: Exception | None = None,
) -> str:
    if isinstance(exc, ParsingFailure):
        return exc.reason

    blocked_reason = detect_html_block_reason(html)
    if blocked_reason:
        return compose_reason(fallback, blocked_reason)

    if exc is not None:
        return compose_reason(fallback, exc.__class__.__name__.lower())

    return fallback
