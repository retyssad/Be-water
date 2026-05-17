# -*- coding: utf-8 -*-
"""通用辅助函数"""
import uuid
from datetime import datetime, timedelta
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """生成唯一 ID（32位 UUID）"""
    uid = uuid.uuid4().hex[:32]
    return f"{prefix}{uid}" if prefix else uid


def now_str() -> str:
    """当前时间的 ISO 格式字符串"""
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def now() -> datetime:
    return datetime.utcnow()


def expires_at(minutes: int = 30) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutes)


def truncate(text: str, max_chars: int = 2000) -> str:
    """截断文本至最大字符数"""
    if text is None:
        return None
    return text[:max_chars] if len(text) > max_chars else text


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """余弦相似度计算"""
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = sum(a * a for a in vec_a) ** 0.5
    norm_b = sum(b * b for b in vec_b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
