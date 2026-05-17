# -*- coding: utf-8 -*-
"""限流中间件（报告第12章）"""
import time
from functools import wraps
from flask import request, jsonify
from config.settings import settings

_visit_records: dict[str, list] = {}


def rate_limit(limit: int = None, window: int = 60):
    """滑动窗口限流"""
    limit = limit or settings.rate_limit_per_minute

    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            ip = request.remote_addr or "unknown"
            now = time.time()
            records = _visit_records.setdefault(ip, [])
            records[:] = [t for t in records if now - t < window]
            if len(records) >= limit:
                return jsonify({"error_code": "SYSTEM003", "message": "请求频率超限"}), 429
            records.append(now)
            return f(*args, **kwargs)
        return wrapper
    return decorator
