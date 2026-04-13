import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DeviceBase(BaseModel):
    name: str
    device_type: str
    location: Optional[str] = None


class DeviceCreate(DeviceBase):
    pass


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    device_type: Optional[str] = None
    location: Optional[str] = None


class DeviceRead(DeviceBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}
