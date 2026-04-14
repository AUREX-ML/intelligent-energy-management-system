from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.database import get_db
from app.models.device import Device
from app.models.telemetry import TelemetryRecord

router = APIRouter()

class TelemetryPayload(BaseModel):
    device_identifier: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime              # Source device timestamp (UTC)
    message_id: Optional[str] = None

VALID_METRICS = {
    "voltage", "current", "active_power", "reactive_power",
    "apparent_power", "power_factor", "frequency",
    "cumulative_energy", "demand"
}

@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_telemetry(payload: TelemetryPayload, db: Session = Depends(get_db)):
    """
    FR-8: Ingest telemetry via HTTP.
    FR-9: Validate required fields.
    FR-10: Reject/quarantine malformed records.
    FR-12: Deduplicate using device_id + metric + timestamp.
    """
    # FR-9 Validate metric type
    if payload.metric_name not in VALID_METRICS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid metric_name '{payload.metric_name}'"
        )

    # Lookup device by identifier
    device = db.query(Device).filter(
        Device.device_identifier == payload.device_identifier,
        Device.is_active == True
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    # FR-12: Deduplication check
    existing = db.query(TelemetryRecord).filter(
        TelemetryRecord.device_id == device.id,
        TelemetryRecord.metric_name == payload.metric_name,
        TelemetryRecord.source_timestamp == payload.timestamp
    ).first()
    if existing:
        return {"status": "duplicate", "message": "Record already exists"}

    record = TelemetryRecord(
        device_id=device.id,
        metric_name=payload.metric_name,
        value=payload.value,
        unit=payload.unit,
        source_timestamp=payload.timestamp,
        is_valid=True,
        quality_flag="good"
    )
    db.add(record)

    # Update device last seen — FR-14, FR-15
    device.last_seen_at = datetime.utcnow()
    device.status = "online"
    db.commit()

    return {"status": "accepted"}

@router.get("/{device_identifier}")
def get_device_telemetry(
    device_identifier: str,
    metric: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Return recent telemetry for a device — FR-1, FR-6."""
    device = db.query(Device).filter(
        Device.device_identifier == device_identifier
    ).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    query = db.query(TelemetryRecord).filter(TelemetryRecord.device_id == device.id)
    if metric:
        query = query.filter(TelemetryRecord.metric_name == metric)

    records = query.order_by(TelemetryRecord.source_timestamp.desc()).limit(limit).all()
    return records