# -*- coding: utf-8 -*-
"""文本问答 / 语音问答 API"""
from flask import jsonify, request
from app.api.v1 import api_bp


@api_bp.route("/chat", methods=["POST"])
def chat():
    """文本问答：直接调用 LLM 返回答案"""
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error_code": "P001", "message": "请输入问题"}), 400

    # 调用核心问答引擎
    from app.core.core_interaction import CoreInteraction
    ci = CoreInteraction()
    ci.initialize()

    try:
        result = ci.process_question(question, "web-session", [])
        return jsonify({
            "answer": result["answer"],
            "sources": result.get("sources", []),
            "confidence": result.get("confidence", 0),
        })
    except Exception as e:
        return jsonify({"error_code": "SYSTEM001", "message": str(e)}), 500


@api_bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """流式对话接口（SSE 简化版，等待 DeepSeek 实际 streaming 实现）"""
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error_code": "P001", "message": "请输入问题"}), 400

    from app.core.core_interaction import CoreInteraction
    ci = CoreInteraction()
    ci.initialize()
    result = ci.process_question(question, "web-session", [])

    return jsonify({
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "confidence": result.get("confidence", 0),
    })
