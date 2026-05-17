# -*- coding: utf-8 -*-
"""ASR 服务封装 — 百度智能云语音识别"""
import base64
import json
import logging
import time
from typing import Optional
import requests
from app.services.base import BaseService
from app.services.circuit_breaker import CircuitBreaker
from config.settings import settings

logger = logging.getLogger("asr_service")

# 百度 OAuth token 缓存
_token_cache: dict = {}


class ASRService(BaseService):
    """语音识别服务：百度短语音识别"""

    def __init__(self):
        super().__init__(service_name="ASR")
        self._cb = CircuitBreaker(name="ASR", failure_threshold=3, recovery_timeout=30.0)
        self._api_key = settings.asr_api_key
        self._secret_key = settings.asr_secret_key
        self._app_id = settings.asr_app_id

    def _get_access_token(self) -> Optional[str]:
        """获取百度 OAuth access_token（带缓存）"""
        if not self._api_key or not self._secret_key:
            return None

        cache_key = f"{self._api_key}:{self._secret_key}"
        cached = _token_cache.get(cache_key)
        if cached and cached["expires_at"] > time.time():
            return cached["token"]

        try:
            url = "https://aip.baidubce.com/oauth/2.0/token"
            params = {
                "grant_type": "client_credentials",
                "client_id": self._api_key,
                "client_secret": self._secret_key,
            }
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            token = data.get("access_token")
            expires_in = data.get("expires_in", 2592000)
            if token:
                _token_cache[cache_key] = {
                    "token": token,
                    "expires_at": time.time() + expires_in - 300,  # 提前 5 分钟刷新
                }
                logger.info("Baidu access token obtained, expires in %ds", expires_in)
                return token
        except Exception as e:
            logger.error("Failed to get Baidu access token: %s", e)
        return None

    def call(self, audio_data: bytes, sample_rate: int = 16000) -> dict:
        """调用百度短语音识别 API"""
        return self._cb.call(self._do_recognize, audio_data, sample_rate)

    def _do_recognize(self, audio_data: bytes, sample_rate: int) -> dict:
        if not self._api_key or not self._secret_key:
            logger.warning("Baidu ASR credentials not configured")
            return self._fallback_response()

        token = self._get_access_token()
        if not token:
            logger.warning("Baidu ASR token unavailable")
            return self._fallback_response()

        # 诊断日志
        duration = len(audio_data) / (sample_rate * 2)  # 16bit = 2 bytes/sample
        logger.info("ASR request: size=%d bytes rate=%d duration=%.1fs",
                     len(audio_data), sample_rate, duration)
        if duration < 0.5:
            logger.warning("Audio too short (%.1fs), may fail recognition", duration)

        # 将 PCM 编码为 WAV 格式的 base64（百度需要特定格式头）
        speech_b64 = base64.b64encode(audio_data).decode("utf-8")

        payload = {
            "format": "pcm",
            "rate": sample_rate,
            "channel": 1,
            "cuid": self._app_id or "water-assistant",
            "token": token,
            "speech": speech_b64,
            "len": len(audio_data),
        }

        try:
            resp = requests.post(
                "https://vop.baidu.com/server_api",
                json=payload,
                timeout=30,
            )
            data = resp.json()
            logger.info("Baidu ASR response: err_no=%s err_msg=%s result_count=%d",
                         data.get("err_no"), data.get("err_msg"),
                         len(data.get("result", [])))

            if data.get("err_no") == 0:
                result = data.get("result", [""])
                text = "".join(result)
                return {"text": text, "confidence": 0.95}
            else:
                err_no = data.get("err_no")
                err_msg = data.get("err_msg", "unknown")
                logger.error("Baidu ASR error [err_no=%s]: %s | audio_size=%d rate=%d",
                             err_no, err_msg, len(audio_data), sample_rate)
                if err_no == 3301:
                    logger.error("Audio quality too poor or format mismatch")
                elif err_no == 3307:
                    logger.error("Audio too short (need > 0.5s of speech)")
                return self._fallback_response()

        except requests.exceptions.Timeout:
            logger.error("Baidu ASR timeout")
            return self._fallback_response()
        except Exception as e:
            logger.error("Baidu ASR error: %s", e)
            return self._fallback_response()

    def _fallback_response(self) -> dict:
        return {"text": "", "confidence": 0.0}

    def health_check(self) -> bool:
        if not self._api_key or not self._secret_key:
            return True
        token = self._get_access_token()
        return token is not None
