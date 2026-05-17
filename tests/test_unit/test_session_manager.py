# -*- coding: utf-8 -*-
"""会话管理单元测试"""
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.core.session_manager import SessionManager


def test_create_and_get_session():
    mgr = SessionManager()
    mgr.initialize()

    session_id = mgr.create_session(user_id="user-001", device_info={"type": "mobile"})
    assert session_id is not None
    assert session_id.startswith("S")

    ctx = mgr.get_session(session_id)
    assert ctx is not None
    assert ctx.user_id == "user-001"


def test_session_expiry():
    mgr = SessionManager()
    mgr.initialize()

    session_id = mgr.create_session(user_id="user-002")
    from app.utils.helpers import now
    import datetime
    # 手动将会话过期时间设为过去
    ctx = mgr._store.get(session_id)
    ctx.expired_at = now() - datetime.timedelta(minutes=1)

    expired = mgr.get_session(session_id)
    assert expired is None


def test_user_sessions():
    mgr = SessionManager()
    mgr.initialize()

    mgr.create_session(user_id="user-003")
    mgr.create_session(user_id="user-003")
    sessions = mgr.get_user_sessions("user-003")
    assert len(sessions) == 2


def test_delete_session():
    mgr = SessionManager()
    mgr.initialize()

    session_id = mgr.create_session(user_id="user-004")
    assert mgr.get_session(session_id) is not None

    mgr.delete_session(session_id)
    assert mgr.get_session(session_id) is None
