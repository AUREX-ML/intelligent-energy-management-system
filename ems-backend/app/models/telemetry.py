from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from app.database import Base

class TelemetryRecord(Base):
    __tablename__ = "telemetry_records"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True)
    metric_name = Column(String, nullable=False)    # voltage, current, active_power, etc.
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    source_timestamp = Column(DateTime, nullable=False)   # Original device timestamp (UTC)
    received_at = Column(DateTime, default=datetime.utcnow)
    is_valid = Column(Boolean, default=True)
    quality_flag = Column(String, default="good")         # good, missing, duplicate, invalid