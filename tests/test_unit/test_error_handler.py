# -*- coding: utf-8 -*-
"""错误处理单元测试"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.error_handler import ErrorHandler


def test_format_error_response():
    handler = ErrorHandler()
    handler.initialize()

    resp = handler.format_error_response("P001")
    assert resp["error_code"] == "P001"
    assert "message" in resp


def test_known_error_code():
    handler = ErrorHandler()
    handler.initialize()

    resp = handler.format_error_response("P001")
    assert resp["error_code"] == "P001"


def test_retry_operation_success():
    handler = ErrorHandler()
    handler.initialize()

    call_count = 0

    def succeed():
        nonlocal call_count
        call_count += 1
        return "done"

    result = handler.retry_operation(succeed, max_retries=3)
    assert result == "done"
    assert call_count == 1  # 第一次就成功


def test_retry_operation_eventually_fails():
    handler = ErrorHandler()
    handler.initialize()

    call_count = 0

    def always_fail():
        nonlocal call_count
        call_count += 1
        raise ValueError("fail")

    import pytest
    with pytest.raises(RuntimeError, match="all retries exhausted"):
        handler.retry_operation(always_fail, max_retries=3)
    assert call_count == 3  # max_retries = total attempts
