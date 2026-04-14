from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.device import DeviceStatus


class DeviceCreate(BaseModel):
    """FR-52: Register a device with all required commissioning fields."""
    device_identifier: str
    device_type: str                        # smart_meter | submeter | sensor
    protocol: str                           # mqtt | http
    building_id: int
    location_description: Optional[str] = None
    heartbeat_interval_seconds: int = 60
    is_controllable: bool = False
    is_safety_critical: bool = False


class DeviceUpdate(BaseModel):
    """FR-55: Allow updating device metadata; all fields optional."""
    device_type: Optional[str] = None
    protocol: Optional[str] = None
    location_description: Optional[str] = None
    heartbeat_interval_seconds: Optional[int] = None
    is_controllable: Optional[bool] = None
    is_safety_critical: Optional[bool] = None
    is_active: Optional[bool] = None


class DeviceRead(BaseModel):
    """FR-14: Full device registry record."""
    id: int
    device_identifier: str
    device_type: str
    protocol: str
    building_id: int
    location_description: Optional[str]
    heartbeat_interval_seconds: int
    status: DeviceStatus
    last_seen_at: Optional[datetime]
    commissioned_at: datetime
    is_active: bool
    is_controllable: bool
    is_safety_critical: bool

    model_config = {"from_attributes": True}
