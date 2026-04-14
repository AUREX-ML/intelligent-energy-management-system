import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from app.database import Base


class CommandType(str, enum.Enum):
    on = "on"
    off = "off"
    schedule_enable = "schedule_enable"
    schedule_disable = "schedule_disable"
    setpoint_change = "setpoint_change"
    mode_change = "mode_change"


class CommandStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    acknowledged = "acknowledged"
    failed = "failed"
    cancelled = "cancelled"


class ControlAction(Base):
    __tablename__ = "control_actions"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    issuer_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)   # null if automated
    command_type = Column(Enum(CommandType), nullable=False)
    command_payload = Column(Text, nullable=True)                             # JSON for setpoint/mode details
    status = Column(Enum(CommandStatus), default=CommandStatus.pending)
    is_automated = Column(Boolean, default=False)                             # FR-46: rule-based automation
    automation_rule_id = Column(Integer, nullable=True)                       # ref to future rule table
    is_override = Column(Boolean, default=False)                              # FR-49: manual override of automation
    issued_at = Column(DateTime, default=datetime.utcnow)
    acknowledged_at = Column(DateTime, nullable=True)
    result_message = Column(String, nullable=True)                            # FR-51: result / ack from device
