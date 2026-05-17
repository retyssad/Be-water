# -*- coding: utf-8 -*-
"""TTS 服务封装 — 百度智能云语音合成"""
import json
import logging
import time
from typing import Optional
import requests
from app.services.base import BaseService
from app.services.circuit_breaker import CircuitBreaker
from config.settings import settings

logger = logging.getLogger("tts_service")

MAX_TEXT_LENGTH = 500  # 单次合成最大字符数


class TTSService(BaseService):
    """语音合成服务：百度短文本合成"""

    def __init__(self):
        super().__init__(service_name="TTS")
        self._cb = CircuitBreaker(name="TTS", failure_threshold=3, recovery_timeout=30.0)
        self._api_key = settings.tts_api_key
        self._secret_key = settings.tts_secret_key
        self._app_id = settings.tts_app_id

    def _get_access_token(self) -> Optional[str]:
        """获取百度 OAuth access_token"""
        if not self._api_key or not self._secret_key:
            return None

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
            return data.get("access_token")
        except Exception as e:
            logger.error("TTS token failed: %s", e)
        return None

    def call(self, text: str, voice_type: str = "female",
             speed: float = 5, volume: int = 5) -> bytes:
        """调用百度 TTS API，返回 WAV 音频数据"""
        return self._cb.call(self._do_synthesize, text, voice_type, speed, volume)

    def _do_synthesize(self, text: str, voice_type: str,
                       speed: float, volume: int) -> bytes:
        if not self._api_key or not self._secret_key:
            logger.warning("Baidu TTS credentials not configured")
            return self._fallback_synthesize(text)

        token = self._get_access_token()
        if not token:
            return self._fallback_synthesize(text)

        # 百度 TTS 参数映射
        speed_val = int(max(0, min(15, speed)))
        volume_val = int(max(0, min(15, volume)))
        voice_map = {"female": 0, "male": 1, "duxiaoyao": 4, "dumeilian": 3}
        per = voice_map.get(voice_type, 0)

        params = {
            "tex": text,
            "tok": token,
            "cuid": self._app_id or "water-assistant",
            "ctp": "1",
            "lan": "zh",
            "spd": speed_val,
            "vol": volume_val,
            "per": per,
            "aue": "6",   # WAV 格式
        }

        try:
            resp = requests.post(
                "https://tsn.baidu.com/text2audio",
                data=params,
                timeout=30,
            )
            if resp.headers.get("Content-Type") == "audio/wav":
                logger.info("TTS success: %d bytes", len(resp.content))
                return resp.content
            else:
                # 百度返回 JSON 错误
                try:
                    err = resp.json()
                    logger.error("Baidu TTS error: %s", err)
                except Exception:
                    logger.error("Baidu TTS returned non-audio response")
                return self._fallback_synthesize(text)
        except requests.exceptions.Timeout:
            logger.error("Baidu TTS timeout")
            return self._fallback_synthesize(text)
        except Exception as e:
            logger.error("Baidu TTS error: %s", e)
            return self._fallback_synthesize(text)

    def _fallback_synthesize(self, text: str) -> bytes:
        """无 API 时的静音音频"""
        return b"\x00\x00" * int(8000 * max(len(text) * 0.15, 1.0))

    def health_check(self) -> bool:
        if not self._api_key or not self._secret_key:
            return True
        token = self._get_access_token()
        return token is not None
