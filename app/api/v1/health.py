# -*- coding: utf-8 -*-
"""健康检查 API（报告 5.3.12）"""
from flask import jsonify
from app.api.v1 import api_bp


@api_bp.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "service": "water-conservancy-assistant",
        "version": "2.0.0",
        "timestamp": __import__("datetime").datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
