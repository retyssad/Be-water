from sqlalchemy import Column, String, Integer, Text, DateTime, func
from app.models.base import Base


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    feedback_id = Column(String(64), primary_key=True)
    session_id = Column(String(64))
    message_id = Column(String(64))
    user_id = Column(String(64))
    rating = Column(Integer)
    feedback_type = Column(String(50))
    comment = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
