# -*- coding: utf-8 -*-
"""应用入口"""
import os
import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app import create_app

app = create_app()

if __name__ == "__main__":
    debug = os.environ.get("WCA_DEBUG", "false").lower() == "true"
    port = int(os.environ.get("WCA_PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=debug)
