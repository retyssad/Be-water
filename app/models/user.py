from sqlalchemy import Column, String, DateTime, func
from app.models.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password_hash = Column(String(256), nullable=False)
    email = Column(String(200))
    phone = Column(String(20))
    role = Column(String(20), default="user")
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime)
    status = Column(String(20), default="active")
