# Тесты случайной паузы jitter - антифрод слой не шлёт запросы в один ритм.
# Проверяем формулу через подмену random.uniform - без флаки от настоящего random.

from unittest.mock import patch

import pytest

from root.shared.net.timeout import random_delay_in_jitter_range


@patch("root.shared.net.timeout.random.uniform", return_value=0.0)
def test_random_delay_at_minimum_when_uniform_zero(mock_uniform):
    # uniform вернул 0 - итог ровно нижняя граница
    assert random_delay_in_jitter_range(0.5, 2.0) == pytest.approx(0.5)
    mock_uniform.assert_called_once_with(0.0, 1.5)


@patch("root.shared.net.timeout.random.uniform", return_value=1.5)
def test_random_delay_at_maximum_when_uniform_full_span(mock_uniform):
    # uniform вернул весь интервал - итог верхняя граница
    assert random_delay_in_jitter_range(0.5, 2.0) == pytest.approx(2.0)


def test_random_delay_when_min_equals_max():
    # Нет разброса - одна константная задержка
    assert random_delay_in_jitter_range(1.0, 1.0) == pytest.approx(1.0)
