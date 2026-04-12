# Модель политики одного HTTP-запроса: TLS impersonate, пауза jitter, опциональные заголовки.

from dataclasses import dataclass, field

from root.shared.http_policy.errors import HttpProfileError


@dataclass(frozen=True)
class HttpProfile:
    impersonate: str
    jitter_min_seconds: float
    jitter_max_seconds: float
    headers: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.jitter_min_seconds < 0:
            raise HttpProfileError(
                f"jitter_min_seconds должен быть ≥ 0, получено: {self.jitter_min_seconds}"
            )
        if self.jitter_max_seconds < 0:
            raise HttpProfileError(f"jitter_max_seconds должен быть ≥ 0, получено: {self.jitter_max_seconds}")
        if self.jitter_min_seconds > self.jitter_max_seconds:
            raise HttpProfileError(
                f"jitter_min_seconds должен быть ≤ jitter_max_seconds, получено: {self.jitter_min_seconds} > {self.jitter_max_seconds}"
            )
        if self.impersonate == "":
            raise HttpProfileError("impersonate не может быть пустой строкой")

AvitoHttpProfile = HttpProfile(
    impersonate='chrome131',
    jitter_min_seconds=0.5,
    jitter_max_seconds=1.5,
)