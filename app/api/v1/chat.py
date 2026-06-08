# -*- coding: utf-8 -*-
"""文本问答 / 语音问答 API"""
import json
import logging
from flask import jsonify, request, Response, stream_with_context
from app.api.v1 import api_bp

logger = logging.getLogger("chat_api")


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
    """流式对话接口（SSE）：逐 token 推送 DeepSeek 生成结果。
    客户端关闭连接即视为打断。"""
    data = request.get_json(silent=True) or {}
    question = data.get("question", "").strip()
    if not question:
        return jsonify({"error_code": "P001", "message": "请输入问题"}), 400

    history = data.get("history", [])
    temperature = float(data.get("temperature", 0.3))
    top_p = float(data.get("top_p", 0.85))

    def generate():
        from app.services.llm_service import LLMService
        svc = LLMService()
        full_answer = []
        try:
            for token in svc.stream_generate(
                prompt=question,
                history=history,
                temperature=temperature,
                top_p=top_p,
            ):
                full_answer.append(token)
                yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"

            # 流结束，发送完整答案
            complete_text = "".join(full_answer)
            logger.info("Stream complete: %d tokens, %d chars",
                       len(full_answer), len(complete_text))
            yield f"data: {json.dumps({'done': True, 'answer': complete_text}, ensure_ascii=False)}\n\n"

        except GeneratorExit:
            logger.info("Client disconnected (interrupted), %d tokens sent", len(full_answer))
            partial = "".join(full_answer) + "\n\n[已打断]"
            yield f"data: {json.dumps({'done': True, 'answer': partial, 'interrupted': True}, ensure_ascii=False)}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "X-Accel-Buffering": "no",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
