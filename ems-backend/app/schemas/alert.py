import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertBase(BaseModel):
    severity: str  # info, warning, critical
    message: str


class AlertCreate(AlertBase):
    device_id: uuid.UUID


class AlertUpdate(BaseModel):
    is_resolved: Optional[bool] = None


class AlertRead(AlertBase):
    id: uuid.UUID
    device_id: uuid.UUID
    is_resolved: bool
    triggered_at: datetime
    resolved_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
