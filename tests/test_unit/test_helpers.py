# -*- coding: utf-8 -*-
"""工具函数单元测试"""
import sys
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.utils.helpers import generate_id, now_str, expires_at, truncate, cosine_similarity


def test_generate_id():
    uid = generate_id()
    assert isinstance(uid, str)
    assert len(uid) == 32  # 16 bytes hex


def test_now_str():
    s = now_str()
    assert isinstance(s, str)
    assert "T" in s


def test_expires_at():
    result = expires_at(minutes=30)
    assert isinstance(result, datetime)


def test_truncate():
    # truncate returns text up to max_chars without appending "..."
    assert truncate("hello world", 5) == "hello"
    assert truncate("hello", 10) == "hello"
    assert truncate(None, 5) is None


def test_cosine_similarity():
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0, 3.0]
    c = [0.0, 0.0, 0.0]
    assert cosine_similarity(a, b) == 1.0
    assert cosine_similarity(a, c) == 0.0
