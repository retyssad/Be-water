# -*- coding: utf-8 -*-
"""请求日志中间件"""
import logging
import time
from flask import request

logger = logging.getLogger("request")


def log_request(response):
    """记录每次请求的日志"""
    duration = time.time() - request.environ.get("_request_start", time.time())
    logger.info("%s %s -> %s (%.0fms)",
                request.method, request.path, response.status_code, duration * 1000)
    return response
