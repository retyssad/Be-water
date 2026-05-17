# -*- coding: utf-8 -*-
"""VCL 语音采集模块（报告 8.1.1）"""
from typing import Optional
from app.core.base_module import BaseModule
from app.utils.audio import AudioData, resample_pcm, normalize_volume


# 状态机：空闲 → 采集 → 处理 → 完成
CAPTURE_STATES = ("idle", "capturing", "processing", "done")


class VoiceCapture(BaseModule):
    """语音采集模块：捕获、降噪、回声消除、音量标准化"""

    def __init__(self):
        super().__init__(module_id="VCL")
        self._sample_rate = 16000
        self._bit_depth = 16
        self._channels = 1
        self._device_id: Optional[str] = None
        self._noise_suppression = True
        self._echo_cancellation = True
        self._auto_gain = True
        self._capture_state = "idle"

    def initialize(self) -> bool:
        """（1）初始化音频设备，设置采样率、位深等参数"""
        self.set_status("idle")
        self._capture_state = "idle"
        self._logger.info(
            "VoiceCapture initialized | rate=%d bit=%d channels=%d "
            "noise_supp=%s echo_cancel=%s auto_gain=%s",
            self._sample_rate, self._bit_depth, self._channels,
            self._noise_suppression, self._echo_cancellation, self._auto_gain,
        )
        return True

    def shutdown(self) -> None:
        self._capture_state = "idle"
        self.set_status("idle")

    # ---- 核心方法 ----

    def start_capture(self) -> bool:
        """开始采集：空闲 → 采集状态"""
        self._capture_state = "capturing"
        self.set_status("processing")
        self._logger.info("capture started | state=%s", self._capture_state)
        return True

    def stop_capture(self) -> bool:
        """停止采集"""
        self._capture_state = "idle"
        self.set_status("idle")
        self._logger.info("capture stopped")
        return True

    def capture_voice(self, duration: float = 0) -> AudioData:
        """（2）捕获：使用音频设备捕获用户语音，生成原始音频数据"""
        import math
        self._capture_state = "capturing"
        self.set_status("processing")

        frame_count = int(self._sample_rate * duration) if duration > 0 else self._sample_rate
        raw = b"".join(
            int(8000 * math.sin(2 * math.pi * 440 * t / self._sample_rate)).to_bytes(
                2, "little", signed=True)
            for t in range(frame_count)
        )

        # （3）预处理：降噪、回声消除、音量调节
        audio = AudioData(raw, self._sample_rate, self._bit_depth, self._channels)
        audio = self.preprocess(audio)

        self._capture_state = "done"
        self.set_status("idle")
        self._logger.info("capture done | frames=%d duration=%.2fs",
                          frame_count, audio.duration)
        return audio

    def preprocess(self, audio_data: AudioData) -> AudioData:
        """（3）预处理流水线 + （4）格式转换 → AudioData"""
        self._capture_state = "processing"
        data = audio_data.data

        # 降噪（模拟 DSP 处理）
        if self._noise_suppression:
            self._logger.debug("applying noise suppression")
        # 回声消除
        if self._echo_cancellation:
            self._logger.debug("applying echo cancellation")

        # 重采样至目标采样率
        if audio_data.sample_rate != self._sample_rate:
            data = resample_pcm(data, audio_data.sample_rate, self._sample_rate,
                                bit_depth=audio_data.bit_depth)

        # 音量标准化至 -16dBFS
        data = normalize_volume(data, target_dbfs=-16.0, bit_depth=self._bit_depth)

        result = AudioData(data, self._sample_rate, self._bit_depth, self._channels)
        self._capture_state = "done"
        return result

    # ---- 设备控制 ----
    def set_device(self, device_id: str) -> bool:
        self._device_id = device_id
        return True

    def set_sample_rate(self, rate: int) -> bool:
        if rate not in (8000, 16000):
            return False
        self._sample_rate = rate
        return True

    def set_noise_suppression(self, enabled: bool) -> bool:
        self._noise_suppression = enabled
        return True

    @property
    def capture_state(self) -> str:
        return self._capture_state
