from sqlalchemy import Column, String, Text, DateTime, func
from app.models.base import Base


class Config(Base):
    __tablename__ = "configs"

    config_id = Column(String(64), primary_key=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text)
    type = Column(String(20))
    description = Column(String(500))
    last_updated = Column(DateTime, server_default=func.now())
    updated_by = Column(String(64))
