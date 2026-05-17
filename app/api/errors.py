# -*- coding: utf-8 -*-
"""统一错误响应"""
from flask import Flask, jsonify


def register_error_handlers(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error_code": "P001", "message": "请求参数错误"}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error_code": "S003", "message": "未授权或会话已过期"}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error_code": "C005", "message": "权限不足"}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error_code": "S001", "message": "资源不存在"}), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error_code": "SYSTEM003", "message": "请求频率超限"}), 429

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"error_code": "SYSTEM001", "message": "系统内部错误"}), 500
