# -*- coding: utf-8 -*-
"""会话管理模块（报告 2.6 / 4.3.2）"""
from typing import Optional
from datetime import datetime, timedelta
from app.core.base_module import BaseModule
from app.utils.helpers import generate_id, expires_at, now


class SessionContext:
    """会话上下文数据结构（报告 4.6.2）"""

    def __init__(self, session_id: str, user_id: str, device_info: dict = None):
        self.session_id = session_id
        self.user_id = user_id
        self.history: list[dict] = []
        self.last_active = now()
        self.expired_at = expires_at(30)
        self.device_info = device_info or {}

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "history": self.history[-10:],  # 滑动窗口
            "last_active": self.last_active.isoformat(),
            "expired_at": self.expired_at.isoformat(),
            "device_info": self.device_info,
        }


class SessionManager(BaseModule):
    """全生命周期管理用户对话"""

    def __init__(self):
        super().__init__(module_id="SessionManager")
        self._store: dict[str, SessionContext] = {}
        self._session_ttl = 30
        self._max_history = 10

    def initialize(self) -> bool:
        self.set_status("idle")
        self._logger.info("SessionManager initialized")
        return True

    def shutdown(self) -> None:
        self._store.clear()
        self.set_status("idle")

    # ---- 核心方法 ----
    def create_session(self, user_id: str, device_info: dict = None) -> str:
        session_id = generate_id(prefix="S")
        ctx = SessionContext(session_id, user_id, device_info)
        self._store[session_id] = ctx
        self._logger.info("session created: %s for user %s", session_id, user_id)
        return session_id

    def get_session(self, session_id: str) -> Optional[SessionContext]:
        ctx = self._store.get(session_id)
        if ctx is None:
            return None
        if now() > ctx.expired_at:
            self._store.pop(session_id, None)
            return None
        ctx.last_active = now()
        return ctx

    def update_session(self, session_id: str, message: dict) -> bool:
        ctx = self.get_session(session_id)
        if ctx is None:
            return False
        ctx.history.append(message)
        if len(ctx.history) > self._max_history:
            ctx.history = ctx.history[-self._max_history:]
        ctx.last_active = now()
        return True

    def delete_session(self, session_id: str) -> bool:
        return self._store.pop(session_id, None) is not None

    def get_user_sessions(self, user_id: str) -> list[str]:
        return [sid for sid, ctx in self._store.items() if ctx.user_id == user_id]

    def clear_expired_sessions(self) -> int:
        before = len(self._store)
        self._store = {k: v for k, v in self._store.items() if now() <= v.expired_at}
        return before - len(self._store)
