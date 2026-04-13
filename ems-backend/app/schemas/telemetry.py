import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TelemetryBase(BaseModel):
    metric: str
    value: float
    unit: Optional[str] = None


class TelemetryCreate(TelemetryBase):
    device_id: uuid.UUID


class TelemetryRead(TelemetryBase):
    id: uuid.UUID
    device_id: uuid.UUID
    recorded_at: datetime

    model_config = {"from_attributes": True}
