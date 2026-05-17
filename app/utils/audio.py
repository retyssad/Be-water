# -*- coding: utf-8 -*-
"""音频处理工具：重采样、PCM/Base64 编解码"""
import base64
import struct
import io
import wave
from typing import Optional


class AudioData:
    """音频数据结构（报告 4.6.1）"""

    def __init__(self, data: bytes, sample_rate: int = 16000,
                 bit_depth: int = 16, channels: int = 1):
        self.data = data
        self.sample_rate = sample_rate
        self.bit_depth = bit_depth
        self.channels = channels

    @property
    def duration(self) -> float:
        """音频时长（秒）"""
        bytes_per_sample = self.bit_depth // 8
        total_samples = len(self.data) / (self.channels * bytes_per_sample)
        return total_samples / self.sample_rate

    def to_base64(self) -> str:
        return base64.b64encode(self.data).decode("utf-8")

    @classmethod
    def from_base64(cls, b64: str, sample_rate: int = 16000,
                    bit_depth: int = 16, channels: int = 1) -> "AudioData":
        return cls(
            data=base64.b64decode(b64),
            sample_rate=sample_rate,
            bit_depth=bit_depth,
            channels=channels,
        )

    def to_wav_bytes(self) -> bytes:
        """导出为 WAV 格式"""
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.bit_depth // 8)
            wf.setframerate(self.sample_rate)
            wf.writeframes(self.data)
        return buf.getvalue()

    def to_dict(self) -> dict:
        return {
            "sample_rate": self.sample_rate,
            "bit_depth": self.bit_depth,
            "channels": self.channels,
            "duration": round(self.duration, 3),
            "format": "PCM",
            "data": self.to_base64(),
        }


def resample_pcm(data: bytes, orig_rate: int, target_rate: int,
                 bit_depth: int = 16) -> bytes:
    """简单重采样（线性插值），适合 8kHz ↔ 16kHz"""
    if orig_rate == target_rate:
        return data
    sample_width = bit_depth // 8
    orig_samples = len(data) // sample_width
    target_samples = int(orig_samples * target_rate / orig_rate)
    fmt_char = "h" if bit_depth == 16 else "b"
    orig_vals = struct.unpack("<" + fmt_char * orig_samples, data)
    result = []
    for i in range(target_samples):
        pos = i * orig_rate / target_rate
        idx = int(pos)
        frac = pos - idx
        if idx + 1 < len(orig_vals):
            val = int(orig_vals[idx] * (1 - frac) + orig_vals[idx + 1] * frac)
        else:
            val = orig_vals[idx]
        result.append(max(-32768, min(32767, val)))
    return struct.pack("<" + fmt_char * len(result), *result)


def normalize_volume(data: bytes, target_dbfs: float = -16.0,
                     bit_depth: int = 16) -> bytes:
    """音量标准化至 target_dbfs"""
    sample_width = bit_depth // 8
    fmt_char = "h" if bit_depth == 16 else "b"
    samples = list(struct.unpack("<" + fmt_char * (len(data) // sample_width), data))
    if not samples:
        return data
    rms = (sum(s * s for s in samples) / len(samples)) ** 0.5
    if rms == 0:
        return data
    current_dbfs = 20 * (rms / 32768 if bit_depth == 16 else rms / 128)
    gain = 10 ** ((target_dbfs - current_dbfs) / 20)
    scaled = [max(-32768, min(32767, int(s * gain))) for s in samples]
    return struct.pack("<" + fmt_char * len(scaled), *scaled)
