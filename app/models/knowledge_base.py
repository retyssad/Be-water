from sqlalchemy import Column, String, Text, Integer, BLOB, DateTime, func
from app.models.base import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    doc_id = Column(String(64), primary_key=True)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    doc_type = Column(String(50), nullable=False)
    category = Column(String(100))
    source = Column(String(200))
    publish_year = Column(Integer)
    embedding_vector = Column(BLOB)
    chunk_index = Column(Integer, default=0)
    total_chunks = Column(Integer, default=1)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now())
    is_active = Column(Integer, default=1)
