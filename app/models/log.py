from sqlalchemy import Column, String, Text, DateTime, func
from app.models.base import Base


class Log(Base):
    __tablename__ = "logs"

    log_id = Column(String(64), primary_key=True)
    level = Column(String(20), nullable=False)
    module = Column(String(100))
    message = Column(Text, nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(String(64))
