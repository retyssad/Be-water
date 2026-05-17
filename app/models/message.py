from sqlalchemy import Column, String, Text, DateTime, ForeignKey, func
from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    message_id = Column(String(64), primary_key=True)
    session_id = Column(String(64), ForeignKey("sessions.session_id"), nullable=False)
    sender = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    message_type = Column(String(20), default="text")
