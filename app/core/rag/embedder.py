# -*- coding: utf-8 -*-
"""Embedding 服务封装（报告 9.2.1）"""
from typing import Optional
from app.core.base_module import BaseModule


class Embedder(BaseModule):
    """Embedding 模型封装：支持 text-embedding-v1 / BGE-large-zh"""

    def __init__(self):
        super().__init__(module_id="Embedder")
        self._model_name = "text-embedding-v1"
        self._dimension = 768

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("Embedder initialized (model=%s, dim=%d)",
                          self._model_name, self._dimension)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    def embed_query(self, text: str) -> list[float]:
        """文本 → {dimension}维向量（基于 SHA256 模拟）"""
        _ = text
        import hashlib, struct
        raw = hashlib.sha256(text.encode()).digest()
        # 重复 hash 直到达到所需维度
        h = bytearray(raw)
        while len(h) < self._dimension * 4:
            h.extend(hashlib.sha256(bytes(h)).digest())
        h = bytes(h[:self._dimension * 4])
        vec = [struct.unpack("f", h[i:i+4])[0] for i in range(0, len(h), 4)]
        norm = sum(v * v for v in vec) ** 0.5
        return [v / norm for v in vec] if norm > 0 else [0.0] * self._dimension

    def embed_documents(self, docs: list) -> list[list[float]]:
        return [self.embed_query(d) for d in docs]
