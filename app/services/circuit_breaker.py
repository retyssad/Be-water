# -*- coding: utf-8 -*-
"""熔断器（报告第11章）"""
import time
import logging
from enum import Enum


class CircuitState(Enum):
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 熔断
    HALF_OPEN = "half_open"  # 半开恢复


class CircuitBreaker:
    """熔断器：3状态 + 滑动窗口错误率检测"""

    def __init__(self, name: str, failure_threshold: int = 5,
                 recovery_timeout: float = 30.0, half_open_max_requests: int = 3):
        self.name = name
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max = half_open_max_requests
        self._half_open_count = 0
        self._last_failure_time = 0.0
        self._logger = logging.getLogger(f"CB-{name}")

    @property
    def state(self) -> CircuitState:
        return self._state

    def call(self, func, *args, **kwargs):
        """熔断保护调用"""
        if self._state == CircuitState.OPEN:
            if time.time() - self._last_failure_time >= self._recovery_timeout:
                self._state = CircuitState.HALF_OPEN
                self._half_open_count = 0
                self._logger.info("circuit half-open: %s", self.name)
            else:
                raise RuntimeError(f"circuit breaker open for {self.name}")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e

    def _on_success(self):
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_count += 1
            if self._half_open_count >= self._half_open_max:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
                self._logger.info("circuit recovered: %s", self.name)
        self._failure_count = 0

    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.time()
        if self._state == CircuitState.HALF_OPEN:
            self._state = CircuitState.OPEN
            self._logger.warning("half-open request failed, back to open: %s", self.name)
        elif self._failure_count >= self._failure_threshold:
            self._state = CircuitState.OPEN
            self._logger.warning("circuit opened: %s (%d failures)",
                                 self.name, self._failure_count)

    def reset(self):
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_count = 0
