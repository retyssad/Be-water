# -*- coding: utf-8 -*-
"""VRL 语音响应模块（报告 8.1.5）"""
from typing import Optional
from app.core.base_module import BaseModule
from app.utils.audio import AudioData

# 状态转换：准备 → 播放 → 完成
PLAYBACK_STATES = ("ready", "playing", "done")


class VoiceResponse(BaseModule):
    """语音响应：播放控制、环境自适应、设备适配"""

    def __init__(self):
        super().__init__(module_id="VRL")
        self._device_id: Optional[str] = None
        self._volume = 80
        self._ambient_noise_level = 50  # 环境噪声 dB
        self._playback_state = "ready"

    def initialize(self) -> bool:
        """（1）初始化音频输出设备，设置音量等参数"""
        self.set_status("idle")
        self._playback_state = "ready"
        self._logger.info("VoiceResponse initialized | device=%s volume=%d",
                          self._device_id or "default", self._volume)
        return True

    def shutdown(self) -> None:
        self.stop_playback()

    # ---- 核心方法 ----

    def play_audio(self, audio_data: AudioData) -> bool:
        """（2）环境适应音量 → （3）播放音频"""
        # （2）根据现场噪声水平自动调节输出音量
        adapted_volume = self._adapt_volume(self._ambient_noise_level)
        self._volume = adapted_volume
        self._logger.debug("ambient noise=%ddB → volume=%d",
                           self._ambient_noise_level, adapted_volume)

        self._playback_state = "playing"
        self.set_status("processing")

        self._logger.info("playing audio | duration=%.2fs volume=%d",
                          audio_data.duration, self._volume)
        return True

    def stop_playback(self) -> bool:
        """停止播放"""
        self._playback_state = "done"
        self.set_status("idle")
        self._logger.info("playback stopped")
        return True

    def get_playback_status(self) -> dict:
        """（4）监控播放状态 / （5）返回播放状态给调用方"""
        return {
            "state": self._playback_state,
            "volume": self._volume,
            "ambient_noise": self._ambient_noise_level,
            "device": self._device_id or "default",
        }

    # ---- 环境自适应 ----
    def set_ambient_noise(self, db_level: float) -> bool:
        """设置当前环境噪声水平（dB）"""
        self._ambient_noise_level = max(20, min(100, db_level))
        return True

    def _adapt_volume(self, noise_db: float) -> int:
        """（2）根据环境噪声自动调节输出音量"""
        if noise_db < 40:
            return 50
        elif noise_db < 60:
            return 70
        elif noise_db < 80:
            return 85
        else:
            return 95

    # ---- 设备控制 ----
    def set_volume(self, volume: int) -> bool:
        self._volume = max(0, min(100, volume))
        return True

    def set_output_device(self, device_id: str) -> bool:
        self._device_id = device_id
        return True

    @property
    def playback_state(self) -> str:
        return self._playback_state
