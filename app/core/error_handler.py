# -*- coding: utf-8 -*-
"""错误处理模块（报告 2.8 / 4.4.2 / 第6章）"""
from typing import Any, Callable, Optional
import time
import logging
from app.core.base_module import BaseModule

# 9 大类错误码（报告第6章）
ERROR_CATEGORIES = {
    "A": "音频相关错误",
    "R": "语音识别错误",
    "P": "核心处理错误",
    "T": "语音合成错误",
    "S": "会话管理错误",
    "C": "配置管理错误",
    "D": "设备相关错误",
    "O": "离线模式错误",
    "SYSTEM": "系统错误",
}


class ErrorHandler(BaseModule):
    """全方位异常处理体系"""

    def __init__(self):
        super().__init__(module_id="ErrorHandler")
        self._error_codes: dict = {}
        self._retry_strategy = {"max_retries": 3, "interval": 1.0}

    def initialize(self) -> bool:
        self._init_error_codes()
        self.set_status("idle")
        self._logger.info("ErrorHandler initialized")
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    def _init_error_codes(self):
        codes = {
            # 音频
            "A001": ("AUDIO_FORMAT_UNSUPPORTED", 400, "音频格式不支持"),
            # 识别
            "R001": ("RECOGNITION_FAILED", 500, "语音识别失败"),
            "R002": ("LOW_CONFIDENCE", 200, "识别置信度低"),
            # 处理
            "P001": ("PROCESSING_FAILED", 500, "核心处理失败"),
            # 合成
            "T001": ("SYNTHESIS_FAILED", 500, "语音合成失败"),
            "T002": ("TEXT_TOO_LONG", 400, "文本过长"),
            # 会话
            "S001": ("SESSION_NOT_FOUND", 404, "会话不存在"),
            "S003": ("SESSION_EXPIRED", 401, "会话已过期"),
            # 配置
            "C001": ("CONFIG_NOT_FOUND", 404, "配置项不存在"),
            "C004": ("REDIS_CONNECTION_FAILED", 503, "Redis连接失败"),
            # 设备
            "D001": ("DEVICE_UNAVAILABLE", 500, "音频设备不可用"),
            # 系统
            "SYSTEM001": ("INTERNAL_ERROR", 500, "系统内部错误"),
            "SYSTEM003": ("RATE_LIMIT_EXCEEDED", 429, "请求频率超限"),
        }
        self._error_codes.update(codes)

    def handle_error(self, error: Exception, context: dict = None) -> dict:
        """处理错误 → ErrorResponse（报告 4.6.3）"""
        error_code = "SYSTEM001"
        for code, (_, _, desc) in self._error_codes.items():
            if desc in str(error):
                error_code = code
                break
        self._logger.error("[%s] %s | context=%s", error_code, error, context)
        return self.format_error_response(error_code, {"detail": str(error)})

    def get_error_message(self, error_code: str) -> str:
        entry = self._error_codes.get(error_code)
        return entry[2] if entry else "未知错误"

    def log_error(self, error: Exception, context: dict = None):
        self._logger.exception("error | context=%s", context)

    def retry_operation(self, operation: Callable, max_retries: int = 3) -> Any:
        """重试策略：最多3次，间隔1s"""
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                self._logger.warning("retry %d/%d failed: %s", attempt + 1, max_retries, e)
                if attempt < max_retries - 1:
                    time.sleep(self._retry_strategy["interval"])
        raise RuntimeError("all retries exhausted")

    def format_error_response(self, error_code: str, details: dict = None) -> dict:
        entry = self._error_codes.get(error_code, ("UNKNOWN", 500, "未知错误"))
        return {
            "error_code": error_code,
            "message": entry[2],
            "http_status": entry[1],
            "details": details or {},
        }
