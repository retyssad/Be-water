# -*- coding: utf-8 -*-
"""数据库初始化脚本"""
import sys
from pathlib import Path

# 将项目根目录加入 sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.db import init_database, get_database_path
from config.settings import settings


def main():
    print("=" * 50)
    print("水利工程技术语音问答助手 - 数据库初始化")
    print("=" * 50)

    # 打印配置信息
    print(f"\n[配置] 数据库路径: {get_database_path()}")
    print(f"[配置] 调试模式: {settings.debug}")
    print(f"[配置] 日志目录: {settings.log_dir}")

    # 确保日志目录存在
    import os
    os.makedirs(settings.log_dir, exist_ok=True)

    # 初始化数据库
    print("\n[执行] 正在创建数据库表...")
    try:
        init_database()
        print("[成功] 数据库初始化完成！")
    except Exception as e:
        print(f"[失败] 数据库初始化出错: {e}")
        sys.exit(1)

    # 验证表是否创建成功
    print("\n[验证] 检查数据库表...")
    from database.db import engine
    import sqlalchemy as sa

    inspector = sa.inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = [
        "users", "sessions", "messages", "configs", "logs",
        "knowledge_base", "terminology", "api_logs",
        "model_evaluation", "user_feedback", "system_metrics",
    ]

    for table in expected_tables:
        if table in tables:
            print(f"  [OK] {table}")
        else:
            print(f"  [!!] {table} (缺失)")

    # 打印统计
    print(f"\n[摘要] 共创建 {len(tables)} 张表")
    print("=" * 50)
    print("数据库初始化完成，可运行以下命令启动服务：")
    print("  python main.py")
    print("=" * 50)


if __name__ == "__main__":
    main()
