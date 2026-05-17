# -*- coding: utf-8 -*-
"""加密工具：AES-256-CBC（报告第12章）"""
import os
import base64
from hashlib import sha256

try:
    from Crypto.Cipher import AES
except ImportError:
    AES = None


def _get_key(secret: str) -> bytes:
    return sha256(secret.encode()).digest()  # 32 bytes for AES-256


def encrypt(plaintext: str, secret: str) -> str:
    """AES-256-CBC 加密 → base64 输出"""
    if AES is None:
        return plaintext
    key = _get_key(secret)
    iv = os.urandom(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = plaintext.encode("utf-8")
    pad_len = 16 - (len(padded) % 16)
    padded += bytes([pad_len] * pad_len)
    ct = cipher.encrypt(padded)
    return base64.b64encode(iv + ct).decode("utf-8")


def decrypt(ciphertext: str, secret: str) -> str:
    """base64 输入 → AES-256-CBC 解密"""
    if AES is None:
        return ciphertext
    key = _get_key(secret)
    raw = base64.b64decode(ciphertext)
    iv, ct = raw[:16], raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    padded = cipher.decrypt(ct)
    pad_len = padded[-1]
    return padded[:-pad_len].decode("utf-8")
