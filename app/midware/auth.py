# -*- coding: utf-8 -*-
"""JWT 认证中间件（报告第12章）"""
import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app

ROLE_HIERARCHY = {"admin": 3, "user": 2, "guest": 1}


def create_token(user_id: str, role: str = "user",
                 secret: str = None, expire_hours: int = 24) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=expire_hours),
    }
    return jwt.encode(payload, secret or "dev-secret", algorithm="HS256")


def require_auth(min_role: str = "user"):
    """认证装饰器"""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"error_code": "S003", "message": "未授权"}), 401
            try:
                token = auth.split(" ", 1)[1]
                payload = jwt.decode(token, options={"verify_signature": False})
                if ROLE_HIERARCHY.get(payload.get("role", "guest"), 0) < ROLE_HIERARCHY.get(min_role, 0):
                    return jsonify({"error_code": "C005", "message": "权限不足"}), 403
                request.user = payload
            except Exception:
                return jsonify({"error_code": "S003", "message": "令牌无效"}), 401
            return f(*args, **kwargs)
        return wrapper
    return decorator
