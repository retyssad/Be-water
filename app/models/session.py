from sqlalchemy import Column, String, DateTime, ForeignKey, func
from app.models.base import Base


class Session(Base):
    __tablename__ = "sessions"

    session_id = Column(String(64), primary_key=True)
    user_id = Column(String(64), ForeignKey("users.user_id"), nullable=False)
    device_id = Column(String(64))
    device_type = Column(String(20))
    start_time = Column(DateTime, server_default=func.now())
    last_active = Column(DateTime, server_default=func.now())
    expired_at = Column(DateTime)
    status = Column(String(20), default="active")
