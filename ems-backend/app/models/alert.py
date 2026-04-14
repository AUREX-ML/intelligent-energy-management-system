import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from app.database import Base

class AlertSeverity(str, enum.Enum):
    informational = "informational"
    warning = "warning"
    high = "high"
    critical = "critical"

class AlertStatus(str, enum.Enum):
    open = "open"
    acknowledged = "acknowledged"
    assigned = "assigned"
    resolved = "resolved"
    closed = "closed"

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    metric_name = Column(String)
    triggered_value = Column(String)
    threshold_condition = Column(String)
    severity = Column(Enum(AlertSeverity), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.open)
    created_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_notes = Column(Text, nullable=True)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)