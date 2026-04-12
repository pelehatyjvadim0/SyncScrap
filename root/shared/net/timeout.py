# Случайная задержка в секундах в диапазоне [min, max] для антифрод-паузы перед запросом.

import random


def random_delay_in_jitter_range(
    jitter_min_seconds: float,
    jitter_max_seconds: float,
) -> float:
    # Равномерное распределение на [min, max]; при min == max возвращает min.
    return jitter_min_seconds + random.uniform(
        0.0,
        jitter_max_seconds - jitter_min_seconds,
    )
