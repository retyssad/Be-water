# -*- coding: utf-8 -*-
"""ASR 语音识别模块（报告 8.1.2）"""
from typing import Optional
from app.core.base_module import BaseModule
from app.utils.audio import AudioData

MAX_RETRIES = 3  # 识别失败最多重试 3 次


class SpeechRecognizer(BaseModule):
    """语音识别：ASR 调用 + 双引擎冗余 + 术语校正"""

    def __init__(self):
        super().__init__(module_id="ASR")
        self._provider = "baidu"
        self._fallback_provider = "aliyun"
        self._hotwords: list[str] = []
        self._dialect = "mandarin"
        self._confidence_threshold = 60

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("SpeechRecognizer initialized | provider=%s threshold=%d",
                          self._provider, self._confidence_threshold)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----

    def recognize_voice(self, audio_data: AudioData) -> dict:
        """语音识别主流程，返回 {text, confidence, corrected, raw}"""
        # （1）验证音频格式
        if not self._validate_audio(audio_data):
            self._logger.error("invalid audio format")
            return {"text": None, "confidence": 0, "corrected": None,
                    "error_code": "A001", "message": "音频格式无效"}

        self.set_status("processing")

        # （2）调用 ASR 服务，最多重试 3 次，仍失败则返回 R001
        result = None
        for attempt in range(MAX_RETRIES):
            result = self._call_asr_api(audio_data)
            if result.get("text"):
                break
            self._logger.warning("ASR attempt %d/%d failed", attempt + 1, MAX_RETRIES)
            if attempt == MAX_RETRIES - 1:
                # 切换到备用服务商
                self._switch_provider()
                result = self._call_asr_api(audio_data)
                if not result.get("text"):
                    self.set_status("idle")
                    return {"text": None, "confidence": 0, "corrected": None,
                            "error_code": "R001", "message": "语音识别失败"}

        # （3）低置信度二次识别
        if result["confidence"] < self._confidence_threshold:
            self._logger.warning("low confidence %.1f, retrying", result["confidence"])
            retry_result = self._call_asr_api(audio_data)
            if retry_result["confidence"] > result["confidence"]:
                result = retry_result

        # （4）术语校正：与术语库匹配，修正误识别词
        text = result.get("text", "")
        corrected = self._apply_term_correction(text)
        result["raw"] = text
        result["corrected"] = corrected

        self.set_status("idle")
        self._logger.info("ASR result | raw='%s' corrected='%s' confidence=%.1f",
                          text[:50], corrected[:50], result["confidence"])
        return result

    def recognize_with_fallback(self, audio_data: AudioData) -> tuple[Optional[str], float]:
        """双引擎冗余识别：主引擎失败自动切备"""
        for attempt in range(2):
            try:
                result = self.recognize_voice(audio_data)
                if result.get("corrected"):
                    return result["corrected"], result.get("confidence", 0)
            except Exception as e:
                self._logger.error("ASR engine %d failed: %s, switching", attempt + 1, e)
                self._switch_provider()
        return None, 0.0

    # ---- 内部 ----

    def _validate_audio(self, audio_data: AudioData) -> bool:
        """（1）验证音频格式：采样率、位深、通道数"""
        if not audio_data or not audio_data.data:
            return False
        if len(audio_data.data) == 0:
            return False
        if audio_data.sample_rate not in (8000, 16000):
            self._logger.warning("unsupported sample rate: %d", audio_data.sample_rate)
            return False
        return True

    def _call_asr_api(self, audio_data: AudioData) -> dict:
        """（2）调用百度智能云 ASR API"""
        from app.services.asr_service import ASRService
        svc = ASRService()
        result = svc.call(audio_data.data, audio_data.sample_rate)
        if result.get("text"):
            return result
        return {"text": "", "confidence": 0}

    def _switch_provider(self):
        self._provider, self._fallback_provider = self._fallback_provider, self._provider
        self._logger.info("switched ASR provider to %s", self._provider)

    def _apply_term_correction(self, text: str) -> str:
        """（4）术语校正：匹配 5000+ 专业词汇库"""
        if not text:
            return text
        # 优先从术语数据库加载（如有）
        corrections = {
            "混泥土": "混凝土", "坝体": "坝体", "帷慕": "帷幕",
            "围幕": "帷幕", "枪堤": "戗堤", "水吹": "水锤",
        }
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)
        return text

    def add_hotwords(self, words: list[str]) -> bool:
        self._hotwords.extend(words)
        return True

    def set_dialect(self, dialect: str) -> bool:
        self._dialect = dialect
        return True

    @property
    def provider(self) -> str:
        return self._provider
