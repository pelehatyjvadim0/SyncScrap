import logging
import time
from collections import deque

from .schemas import (
    RATE_LIMIT_WINDOW_SECONDS,
    RATE_LIMIT_MAX_CALLS,
)

logger = logging.getLogger(__name__)

# Простой rate limiter - sliding window в памяти процесса.
class SlidingWindowRateLimiter:
    def __init__(self, *, max_calls: int, window_seconds: int) -> None:
        self._max_calls = max_calls
        self._window_seconds = window_seconds
        # deque отличный выбор, подрез слева и справа, O(1) сложность, в списке O(n)
        self._events: deque[float] = deque()

    # Проверяем, можно ли принять новый вызов в текущем временном окне.
    def allow(self) -> bool:
        now = time.monotonic()
        while self._events and now - self._events[0] > self._window_seconds:
            self._events.popleft()
        if len(self._events) >= self._max_calls:
            return False
        self._events.append(now)
        return True

# Глобальные экземпляры логики инструмента enqueue_discovery.
rate_limiter = SlidingWindowRateLimiter(
    max_calls=RATE_LIMIT_MAX_CALLS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)
