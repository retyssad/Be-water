# -*- coding: utf-8 -*-
"""限流器单元测试"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from flask import Flask
from app.midware.rate_limiter import rate_limit


def test_rate_limit_decorator():
    """验证限流装饰器在请求上下文中可正常调用"""
    app = Flask(__name__)

    with app.test_request_context():
        decorator = rate_limit(limit=100, window=60)
        assert callable(decorator)

        def dummy():
            return "ok"

        wrapped = decorator(dummy)
        assert callable(wrapped)
        # 首次调用应成功
        result = wrapped()
        assert result == "ok"
