# -*- coding: utf-8 -*-
"""知识库检索 API（报告 5.3.9）"""
from flask import jsonify, request
from app.api.v1 import api_bp
from app.core.rag.rag_engine import RAGEngine

_rag = RAGEngine()


@api_bp.route("/knowledge/retrieve", methods=["POST"])
def retrieve_knowledge():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "")
    if not query:
        return jsonify({"error_code": "P001", "message": "缺少查询内容"}), 400

    _rag.initialize()
    results = _rag.hybrid_search(
        query,
        filters={"category": data.get("filters", {}).get("category")},
    )
    return jsonify({
        "results": results,
        "total": len(results),
    })
