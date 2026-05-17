# -*- coding: utf-8 -*-
"""Flask App Factory"""
import logging
import os
from pathlib import Path
from flask import Flask, send_file

# 配置全局日志，确保 ASR/TTS/LLM 的诊断日志可见
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


def create_app(config_name: str = "default") -> Flask:
    app = Flask(__name__, static_folder="app/static")
    app.config["SECRET_KEY"] = os.environ.get("WCA_SECRET_KEY", "dev-key")
    app.config["JSON_AS_ASCII"] = False  # 支持中文

    # 注册蓝图
    from app.api.v1 import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    # 注册错误处理
    from app.api.errors import register_error_handlers
    register_error_handlers(app)

    # 首页
    @app.route("/")
    def index():
        static_dir = Path(__file__).parent / "static"
        html_path = static_dir / "index.html"
        if html_path.exists():
            return send_file(str(html_path))
        return {"service": "water-conservancy-assistant", "version": "2.0.0", "docs": "/api/v1/health"}

    return app
