# -*- coding: utf-8 -*-
"""大模型参数调优 API（报告 5.3.11）"""
from flask import jsonify, request
from app.api.v1 import api_bp
from config.settings import settings


@api_bp.route("/model/config", methods=["PUT"])
def update_model_config():
    data = request.get_json(silent=True) or {}
    allowed_keys = {"temperature", "top_p", "max_tokens",
                    "rag_top_k", "similarity_threshold"}
    for key, value in data.items():
        if key in allowed_keys:
            settings.set(key, value)
    return jsonify({
        "status": "success",
        "message": "模型配置已更新",
    })
