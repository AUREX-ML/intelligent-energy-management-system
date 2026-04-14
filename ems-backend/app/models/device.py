import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Float, Boolean
from app.database import Base

class DeviceStatus(str, enum.Enum):
    online = "online"
    degraded = "degraded"
    offline = "offline"
    unknown = "unknown"

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_identifier = Column(String, unique=True, nullable=False, index=True)
    device_type = Column(String, nullable=False)          # smart_meter, submeter, sensor
    protocol = Column(String, nullable=False)             # mqtt, http
    building_id = Column(Integer, ForeignKey("buildings.id"), nullable=False)
    location_description = Column(String)
    heartbeat_interval_seconds = Column(Integer, default=60)
    status = Column(Enum(DeviceStatus), default=DeviceStatus.unknown)
    last_seen_at = Column(DateTime, nullable=True)
    commissioned_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_controllable = Column(Boolean, default=False)
    is_safety_critical = Column(Boolean, default=False)