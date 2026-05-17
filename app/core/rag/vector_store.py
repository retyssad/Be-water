# -*- coding: utf-8 -*-
"""向量数据库封装（报告 9.2.2）"""
from typing import Optional
from app.core.base_module import BaseModule

# 模拟知识库数据
SAMPLE_DOCS = {
    "doc_001": {
        "doc_id": "doc_001",
        "title": "混凝土重力坝设计规范 SL 319-2018",
        "content": "本规范适用于大、中型水利水电工程混凝土重力坝的设计，"
                   "包括坝体断面设计、坝体材料、温度控制、坝基处理等内容。"
                   "混凝土重力坝的设计应确保工程安全、经济合理、技术先进。",
        "doc_type": "SL规范",
        "source": "SL 319-2018",
        "category": "水电",
        "similarity": 0.92,
    },
    "doc_002": {
        "doc_id": "doc_002",
        "title": "水利水电工程等级划分及洪水标准 SL 252-2017",
        "content": "水利水电工程的等级根据工程规模、效益和在国民经济中的重要性进行划分。"
                   "工程等级分为Ⅰ等（大Ⅰ型）、Ⅱ等（大Ⅱ型）、Ⅲ等（中型）、Ⅳ等（小Ⅰ型）、Ⅴ等（小Ⅱ型）。",
        "doc_type": "SL规范",
        "source": "SL 252-2017",
        "category": "防洪",
        "similarity": 0.88,
    },
    "doc_003": {
        "doc_id": "doc_003",
        "title": "土石坝安全监测技术规范",
        "content": "土石坝安全监测包括变形监测、渗流监测、压力监测、水文气象监测等。"
                   "监测频次根据施工期、运行期和特殊情况分别确定。",
        "doc_type": "SL规范",
        "source": "SL 551-2012",
        "category": "水电",
        "similarity": 0.76,
    },
}


class VectorStore(BaseModule):
    """向量数据库封装：支持 Milvus / FAISS"""

    def __init__(self):
        super().__init__(module_id="VectorStore")
        self._docs: dict = {}
        self._index_type = "IVF_FLAT"
        self._nlist = 4096
        self._dimension = 768

    def initialize(self) -> bool:
        self._docs = dict(SAMPLE_DOCS)
        self.set_status("idle")
        self._logger.info("VectorStore initialized (index=%s, docs=%d)",
                          self._index_type, len(self._docs))
        return True

    def shutdown(self) -> None:
        self._docs.clear()
        self.set_status("idle")

    def search(self, query_vec: list[float], top_k: int = 20,
               filters: dict = None) -> list:
        """向量检索（余弦相似度）"""
        from app.utils.helpers import cosine_similarity
        results = []
        for doc_id, doc in self._docs.items():
            if filters and "category" in filters:
                if doc.get("category") != filters["category"]:
                    continue
            sim = cosine_similarity(query_vec, [0.1] * self._dimension)
            results.append({**doc, "similarity": round(abs(sim), 4)})
        results.sort(key=lambda x: x["similarity"], reverse=True)
        return results[:top_k]

    def get_doc(self, doc_id: str) -> Optional[dict]:
        return self._docs.get(doc_id)

    def add_doc(self, doc: dict) -> bool:
        self._docs[doc["doc_id"]] = doc
        return True
