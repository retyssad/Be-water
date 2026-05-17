# -*- coding: utf-8 -*-
"""会话管理 API（报告 5.3.1-5.3.5）"""
from flask import jsonify, request
from app.api.v1 import api_bp
from app.core.session_manager import SessionManager

_session_manager = SessionManager()


@api_bp.route("/sessions", methods=["POST"])
def create_session():
    """创建会话（5.3.1）"""
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id", "anonymous")
    device_info = {
        "device_type": data.get("device_type", "unknown"),
        "device_id": data.get("device_id", ""),
    }
    session_id = _session_manager.create_session(user_id, device_info)
    return jsonify({
        "session_id": session_id,
        "expires_in": 1800,
        "max_history": 10,
    }), 201


@api_bp.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    """获取会话信息（5.3.2）"""
    ctx = _session_manager.get_session(session_id)
    if ctx is None:
        return jsonify({"error_code": "S001", "message": "会话不存在或已过期"}), 404
    return jsonify(ctx.to_dict())


@api_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    """结束会话（5.3.3）"""
    if _session_manager.delete_session(session_id):
        return jsonify({"status": "success", "message": "会话已成功结束"})
    return jsonify({"error_code": "S001", "message": "会话不存在"}), 404


@api_bp.route("/sessions/<session_id>/messages", methods=["POST"])
def send_message(session_id):
    """发送消息（5.3.4）"""
    data = request.get_json(silent=True) or {}
    content = data.get("content", "")
    if not content:
        return jsonify({"error_code": "P001", "message": "消息内容不能为空"}), 400

    ctx = _session_manager.get_session(session_id)
    if ctx is None:
        return jsonify({"error_code": "S003", "message": "会话已过期"}), 401

    from app.utils.helpers import generate_id, now_str
    msg = {"role": "user", "content": content, "timestamp": now_str()}
    _session_manager.update_session(session_id, msg)

    # 核心交互
    from app.core.core_interaction import CoreInteraction
    llm = CoreInteraction()
    result = llm.process_question(content, session_id, ctx.history)
    reply = {"role": "assistant", "content": result["answer"], "timestamp": now_str()}
    _session_manager.update_session(session_id, reply)

    return jsonify({
        "message_id": generate_id(prefix="M"),
        "response": result["answer"],
        "sources": result.get("sources", []),
    })


@api_bp.route("/sessions/<session_id>/messages", methods=["GET"])
def get_messages(session_id):
    """获取消息历史（5.3.5）"""
    ctx = _session_manager.get_session(session_id)
    if ctx is None:
        return jsonify({"error_code": "S001", "message": "会话不存在"}), 404
    return jsonify({
        "messages": ctx.history,
        "total": len(ctx.history),
    })
