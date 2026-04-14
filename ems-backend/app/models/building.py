from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from app.database import Base


class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    timezone = Column(String, nullable=False, default="Africa/Nairobi")  # FR-4: site local time
    tariff_structure = Column(Text, nullable=True)        # FR-60: site-specific tariff (JSON string)
    working_schedule = Column(Text, nullable=True)        # FR-60: site-specific schedule (JSON string)
    alert_routing_policy = Column(Text, nullable=True)    # FR-60: alert routing config (JSON string)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
