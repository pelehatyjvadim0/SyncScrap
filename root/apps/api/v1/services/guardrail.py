import re
from typing import Any

_SCAM_HINTS = [
    re.compile(r"предоплат", re.IGNORECASE),
    re.compile(r"telegram|тг|whatsapp", re.IGNORECASE),
    re.compile(r"только сегодня, срочно перевод", re.IGNORECASE),
]


class LocalGuardrail:
    @staticmethod
    def evaluate(payload: dict[str, Any]) -> tuple[bool, float]:
        text = " ".join(
            [
                str(payload.get("title", "")),
                str(payload.get("description_markdown", "")),
            ]
        )
        hits = sum(1 for pattern in _SCAM_HINTS if pattern.search(text))
        scam_score = min(1.0, hits / len(_SCAM_HINTS))
        return scam_score < 0.67, scam_score
