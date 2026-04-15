import time
from collections import defaultdict
from contextlib import contextmanager
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._timings_ms: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    def inc(self, key: str, value: int = 1) -> None:
        with self._lock:
            self._counters[key] += value

    def timing(self, key: str, ms: float) -> None:
        with self._lock:
            self._timings_ms[key].append(ms)

    @contextmanager
    def timer(self, key: str):
        started = time.perf_counter()
        try:
            yield
        finally:
            elapsed = (time.perf_counter() - started) * 1000
            self.timing(key, elapsed)

    def snapshot(self) -> dict:
        with self._lock:
            avg_timings = {
                k: (sum(v) / len(v) if v else 0.0) for k, v in self._timings_ms.items()
            }
            return {"counters": dict(self._counters), "avg_timings_ms": avg_timings}


metrics = MetricsRegistry()
