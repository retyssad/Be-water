# -*- coding: utf-8 -*-
"""音频处理单元测试"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.utils.audio import AudioData, resample_pcm, normalize_volume


def test_audio_data_to_base64():
    audio = AudioData(data=b"\x00\x01\x02\x03", sample_rate=16000, bit_depth=16, channels=1)
    b64 = audio.to_base64()
    assert isinstance(b64, str)
    assert len(b64) > 0


def test_audio_data_roundtrip():
    original = b"\x00\x01\x02\x03"
    audio = AudioData(data=original, sample_rate=16000, bit_depth=16, channels=1)
    b64 = audio.to_base64()
    restored = AudioData.from_base64(b64, sample_rate=16000)
    assert restored.data == original


def test_resample_pcm():
    pcm = b"\x00\x01\x02\x03\x04\x05\x06\x07"
    result = resample_pcm(pcm, orig_rate=8000, target_rate=16000, bit_depth=16)
    assert len(result) > 0


def test_normalize_volume():
    pcm = b"\x00\x10\x20\x30"
    result = normalize_volume(pcm, target_dbfs=-16.0, bit_depth=16)
    assert isinstance(result, bytes)
    assert len(result) > 0
