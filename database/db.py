# -*- coding: utf-8 -*-
"""数据库连接与会话管理"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import NullPool

from config.settings import settings


def get_database_path() -> str:
    """确保数据库目录存在"""
    import os
    path = settings.database_path
    db_dir = os.path.dirname(path)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    return path


DATABASE_URL = f"sqlite:///{get_database_path()}"

engine = create_engine(
    DATABASE_URL,
    echo=settings.debug,
    poolclass=NullPool,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """启用 WAL 模式和外键约束"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


SessionLocal = scoped_session(sessionmaker(bind=engine))


def get_db():
    """获取数据库会话（用于 FastAPI/Flask 依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database():
    """初始化数据库：建表"""
    from database.schema import SCHEMA_SQL
    conn = engine.raw_connection()
    conn.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"[DB] 数据库初始化完成: {get_database_path()}")
