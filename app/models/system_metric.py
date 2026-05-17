from sqlalchemy import Column, String, Float, DateTime, func
from app.models.base import Base


class SystemMetric(Base):
    __tablename__ = "system_metrics"

    metric_id = Column(String(64), primary_key=True)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(20))
    host = Column(String(100))
    recorded_at = Column(DateTime, server_default=func.now())
