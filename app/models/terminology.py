from sqlalchemy import Column, String, Text, DateTime, func
from app.models.base import Base


class Terminology(Base):
    __tablename__ = "terminology"

    term_id = Column(String(64), primary_key=True)
    term = Column(String(100), nullable=False, unique=True)
    pinyin = Column(String(200))
    definition = Column(Text, nullable=False)
    category = Column(String(50))
    source = Column(String(200))
    synonyms = Column(String(500))
    usage_examples = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
