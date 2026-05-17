# -*- coding: utf-8 -*-
"""RAG 检索增强生成引擎（报告 4.5.1 / 9.1）"""
from typing import Optional
from app.core.base_module import BaseModule
from app.core.rag.embedder import Embedder
from app.core.rag.vector_store import VectorStore
from app.utils.helpers import cosine_similarity


class RAGEngine(BaseModule):
    """RAG 引擎：知识外脑 — 混合检索 + 重排序"""

    def __init__(self):
        super().__init__(module_id="RAGEngine")
        self._embedder: Optional[Embedder] = None
        self._vector_store: Optional[VectorStore] = None
        self._top_k = 5
        self._similarity_threshold = 0.75

    def initialize(self) -> bool:
        self._embedder = Embedder()
        self._embedder.initialize()
        self._vector_store = VectorStore()
        self._vector_store.initialize()
        self.set_status("idle")
        self._logger.info("RAGEngine initialized (top_k=%d, threshold=%.2f)",
                          self._top_k, self._similarity_threshold)
        return True

    def shutdown(self) -> None:
        self.set_status("idle")

    # ---- 核心方法 ----
    def hybrid_search(self, query: str, filters: dict = None) -> list:
        """混合检索：向量检索 + BM25 + RRF 融合（报告 9.1.3）"""
        self.set_status("processing")
        query_vec = self._embedder.embed_query(query)

        # 向量检索 top-20
        vec_results = self._vector_store.search(query_vec, top_k=20, filters=filters)

        # BM25 关键词检索 top-20（模拟）
        bm25_results = self._bm25_search(query, top_k=20)

        # RRF 融合
        rrf_scores = self._rrf_fusion(vec_results, bm25_results, k=60)

        # 取 top_k
        merged = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)[:self._top_k]
        results = []
        for doc_id, score in merged:
            doc = self._vector_store.get_doc(doc_id)
            if doc and score >= self._similarity_threshold:
                doc["rrf_score"] = round(score, 4)
                results.append(doc)

        self.set_status("idle")
        return results

    def retrieve(self, query: str, top_k: int = None) -> list:
        """纯向量检索"""
        k = top_k or self._top_k
        query_vec = self._embedder.embed_query(query)
        return self._vector_store.search(query_vec, top_k=k)

    def rerank_results(self, results: list, query: str) -> list:
        """Cross-Encoder 重排序（模拟）"""
        _ = query
        return sorted(results, key=lambda x: x.get("similarity", 0), reverse=True)

    # ---- 内部 ----
    def _bm25_search(self, query: str, top_k: int = 20) -> dict:
        """模拟 BM25 检索"""
        _ = query
        return {"doc_001": 0.85, "doc_002": 0.72, "doc_003": 0.68}

    @staticmethod
    def _rrf_fusion(vec_results: list, bm25_results: dict, k: int = 60) -> dict:
        """Reciprocal Rank Fusion（报告 9.1.3）"""
        scores = {}
        for rank, doc in enumerate(vec_results):
            doc_id = doc.get("doc_id", "")
            scores[doc_id] = 1.0 / (k + rank + 1)
        for rank, (doc_id, _) in enumerate(sorted(bm25_results.items(),
                                                   key=lambda x: x[1], reverse=True)):
            scores[doc_id] = scores.get(doc_id, 0) + 1.0 / (k + rank + 1)
        return scores
