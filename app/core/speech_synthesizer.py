# -*- coding: utf-8 -*-
"""TTS 语音合成模块（报告 8.1.4）"""
from typing import Optional
from app.core.base_module import BaseModule
from app.utils.audio import AudioData

MAX_TEXT_LENGTH = 500  # 单次合成上限
MAX_RETRIES = 3         # 合成失败重试 3 次


class SpeechSynthesizer(BaseModule):
    """语音合成：在线 TTS + 离线兜底 + 后处理"""

    def __init__(self):
        super().__init__(module_id="TTS")
        self._provider = "baidu"
        self._voice_type = "female"  # female / male
        self._speed = 5             # 0-15
        self._volume = 5            # 0-15
        self._pause_long = 0.3      # 长句间隔 (s)
        self._pause_term = 0.2      # 术语后间隔 (s)

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("SpeechSynthesizer initialized | provider=%s voice=%s",
                          self._provider, self._voice_type)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----

    def synthesize_speech(self, text: str) -> AudioData:
        """文本 → 语音（完整流水线）"""
        # （1）验证文本长度（≤500字），超长分段合成
        if len(text) > MAX_TEXT_LENGTH:
            self._logger.info("text too long (%d chars), splitting", len(text))
            return self._synthesize_segments(text)

        self.set_status("processing")

        try:
            audio = self._call_tts_api(text)
            # （4）后处理：停顿标记 → 音量归一化
            audio = self._postprocess(audio)
        except Exception as e:
            self._logger.error("TTS failed: %s", e)
            return self._offline_synthesize(text)

        self.set_status("idle")
        return audio

    # ---- 内部 ----

    def _call_tts_api(self, text: str) -> AudioData:
        """（2）调用 TTS 服务，重试 3 次"""
        from app.services.tts_service import TTSService
        svc = TTSService()

        for attempt in range(MAX_RETRIES):
            try:
                raw = svc.call(text, self._voice_type, self._speed, self._volume)
                if raw and len(raw) > 100:
                    return AudioData(raw, sample_rate=16000)
            except Exception as e:
                self._logger.warning("TTS attempt %d/%d: %s", attempt + 1, MAX_RETRIES, e)

        # 切换离线引擎
        self._logger.warning("all TTS attempts failed, switching to offline")
        return self._offline_synthesize(text)

    def _synthesize_segments(self, text: str) -> AudioData:
        """超长文本分段合成"""
        segments = []
        pos = 0
        while pos < len(text):
            seg = text[pos:pos + MAX_TEXT_LENGTH]
            audio = self._call_tts_api(seg)
            segments.append(audio.data)
            pos += MAX_TEXT_LENGTH

        merged = b"".join(segments)
        return AudioData(merged, sample_rate=16000)

    def _offline_synthesize(self, text: str) -> AudioData:
        """离线轻量合成（占位静音）"""
        raw = b"\x00\x00" * int(8000 * max(len(text) * 0.15, 1.0))
        return AudioData(raw, sample_rate=8000)

    def _postprocess(self, audio_data: AudioData) -> AudioData:
        """（4）音频后处理：音量归一化 + 格式封装"""
        from app.utils.audio import normalize_volume
        data = normalize_volume(audio_data.data, target_dbfs=-16.0,
                                bit_depth=audio_data.bit_depth)
        return AudioData(data, audio_data.sample_rate,
                         audio_data.bit_depth, audio_data.channels)

    # ---- 控制方法 ----
    def set_voice_type(self, voice_type: str) -> bool:
        """设置音色：female / male"""
        self._voice_type = voice_type
        return True

    def set_speed(self, speed: float) -> bool:
        """语速 0-15"""
        self._speed = max(0, min(15, speed))
        return True

    def set_volume(self, volume: int) -> bool:
        """音量 0-15"""
        self._volume = max(0, min(15, volume))
        return True
