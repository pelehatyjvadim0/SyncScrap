# Валидация HttpProfile - отрицательный jitter или min больше max недопустимы для политики запроса.

import pytest

from root.shared.http_policy.errors import HttpProfileError
from root.shared.http_policy.profiles import HttpProfile


def test_http_profile_accepts_valid_jitter_range():
    p = HttpProfile(
        impersonate="chrome131",
        jitter_min_seconds=0.0,
        jitter_max_seconds=1.0,
    )
    assert p.jitter_min_seconds == 0.0
    assert p.impersonate == "chrome131"


def test_http_profile_rejects_negative_jitter_min():
    with pytest.raises(HttpProfileError):
        HttpProfile(
            impersonate="chrome131",
            jitter_min_seconds=-0.1,
            jitter_max_seconds=1.0,
        )


def test_http_profile_rejects_min_greater_than_max():
    with pytest.raises(HttpProfileError):
        HttpProfile(
            impersonate="chrome131",
            jitter_min_seconds=2.0,
            jitter_max_seconds=1.0,
        )


def test_http_profile_rejects_empty_impersonate():
    with pytest.raises(HttpProfileError):
        HttpProfile(
            impersonate="",
            jitter_min_seconds=0.0,
            jitter_max_seconds=0.0,
        )
