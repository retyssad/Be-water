from sqlalchemy import Column, String, Integer, DateTime
from app.models.base import Base


class ApiLog(Base):
    __tablename__ = "api_logs"

    log_id = Column(String(64), primary_key=True)
    session_id = Column(String(64))
    user_id = Column(String(64))
    api_type = Column(String(20), nullable=False)
    provider = Column(String(50))
    request_size = Column(Integer)
    response_size = Column(Integer)
    latency_ms = Column(Integer)
    status_code = Column(Integer)
    error_code = Column(String(20))
    request_time = Column(DateTime, nullable=False)
    cost_ms = Column(Integer)
