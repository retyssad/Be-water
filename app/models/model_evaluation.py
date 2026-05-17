from sqlalchemy import Column, String, Text, Float, Integer, DateTime, func
from app.models.base import Base


class ModelEvaluation(Base):
    __tablename__ = "model_evaluation"

    eval_id = Column(String(64), primary_key=True)
    session_id = Column(String(64))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    retrieved_docs = Column(Text)
    rouge_l = Column(Float)
    bleu_4 = Column(Float)
    term_match_rate = Column(Float)
    hallucination_score = Column(Float)
    user_rating = Column(Integer)
    eval_time = Column(DateTime, server_default=func.now())
