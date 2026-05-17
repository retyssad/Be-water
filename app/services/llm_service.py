# -*- coding: utf-8 -*-
"""LLM 服务封装 — DeepSeek API（OpenAI 兼容）"""
import json
import logging
import requests
from typing import Optional
from app.services.base import BaseService
from app.services.circuit_breaker import CircuitBreaker
from config.settings import settings

logger = logging.getLogger("llm_service")


class LLMService(BaseService):
    """大语言模型服务：DeepSeek 为主，可回落文心/通义"""

    def __init__(self):
        super().__init__(service_name="LLM")
        self._cb = CircuitBreaker(name="LLM", failure_threshold=3, recovery_timeout=60.0)
        self._api_key = settings.llm_api_key
        self._api_base = settings.llm_api_base.rstrip("/")
        self._model = settings.llm_model

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def call(self, prompt: str, temperature: float = 0.3,
             top_p: float = 0.85, max_tokens: int = 2048,
             history: Optional[list] = None,
             system_prompt: Optional[str] = None) -> str:
        """调用 DeepSeek Chat API"""
        return self._cb.call(
            self._do_generate, prompt, temperature,
            top_p, max_tokens, history, system_prompt
        )

    def _build_messages(self, prompt: str, history: Optional[list],
                        system_prompt: Optional[str]) -> list:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "你是水利工程技术领域的专业助手。请基于以下原则回答："
                    "1) 优先引用水利行业规范（SL标准）作为依据；"
                    "2) 涉及计算时展示完整推导过程；"
                    "3) 使用专业术语，必要时附解释；"
                    "4) 不确定的内容请明确说明。"
                ),
            })
        if history:
            for h in history[-10:]:  # 滑动窗口 10 轮
                role = h.get("role", "user")
                content = h.get("content", "")
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _do_generate(self, prompt: str, temperature: float,
                     top_p: float, max_tokens: int,
                     history: Optional[list],
                     system_prompt: Optional[str]) -> str:
        if not self._api_key:
            logger.warning("DeepSeek API key not configured, using fallback")
            return self._fallback_response(prompt)

        messages = self._build_messages(prompt, history, system_prompt)
        payload = {
            "model": self._model,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
            "stream": False,
        }

        try:
            resp = requests.post(
                f"{self._api_base}/v1/chat/completions",
                headers=self._headers,
                json=payload,
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
            answer = data["choices"][0]["message"]["content"]
            logger.info(
                "DeepSeek response: model=%s tokens=%s",
                data.get("model", "unknown"),
                data.get("usage", {}).get("total_tokens", "?"),
            )
            return answer
        except requests.exceptions.Timeout:
            logger.error("DeepSeek API timeout")
            return self._fallback_response(prompt)
        except requests.exceptions.RequestException as e:
            logger.error("DeepSeek API error: %s", e)
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """无 API key 或网络异常时的兜底"""
        return (
            "当前未配置大模型 API Key，以下是基于本地知识库的回答：\n"
            "水利工程的主要类型包括防洪工程、灌溉工程、水力发电工程、"
            "航运工程等。依据《水利水电工程等级划分及洪水标准》SL 252-2017。\n"
            "如需获取基于大模型的精确回答，请配置 DeepSeek API Key。"
        )

    def health_check(self) -> bool:
        if not self._api_key:
            return True  # 无 Key 时依赖兜底，视为可用
        try:
            resp = requests.get(
                f"{self._api_base}/v1/models",
                headers=self._headers,
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False
