from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional
from app.database import get_db
from app.models.telemetry import TelemetryRecord
from app.models.alert import Alert
from app.models.device import Device

router = APIRouter()


@router.get("/energy-summary")
def energy_summary(
    building_id: Optional[int] = Query(None, description="Filter by building"),
    device_id: Optional[int] = Query(None, description="Filter by device"),
    start_date: Optional[date] = Query(None, description="Start of reporting period (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End of reporting period (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
):
    """FR-31, FR-32: Aggregate energy consumption for the requested scope and period."""
    query = (
        db.query(
            TelemetryRecord.metric_name,
            func.sum(TelemetryRecord.value).label("total"),
            func.avg(TelemetryRecord.value).label("average"),
            func.max(TelemetryRecord.value).label("peak"),
            func.min(TelemetryRecord.value).label("minimum"),
            func.count(TelemetryRecord.id).label("sample_count"),
        )
        .filter(TelemetryRecord.is_valid == True)
    )

    if device_id:
        query = query.filter(TelemetryRecord.device_id == device_id)
    elif building_id:
        device_ids = db.query(Device.id).filter(Device.building_id == building_id).subquery()
        query = query.filter(TelemetryRecord.device_id.in_(device_ids))

    if start_date:
        query = query.filter(TelemetryRecord.source_timestamp >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(TelemetryRecord.source_timestamp <= datetime.combine(end_date, datetime.max.time()))

    rows = query.group_by(TelemetryRecord.metric_name).all()

    return {
        "building_id": building_id,
        "device_id": device_id,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "metrics": [
            {
                "metric": r.metric_name,
                "total": r.total,
                "average": r.average,
                "peak": r.peak,
                "minimum": r.minimum,
                "sample_count": r.sample_count,
            }
            for r in rows
        ],
    }


@router.get("/alert-history")
def alert_history(
    building_id: Optional[int] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: Session = Depends(get_db),
):
    """FR-31, FR-32: Return alert history for a building and period."""
    query = db.query(Alert)

    if building_id:
        query = query.filter(Alert.building_id == building_id)
    if start_date:
        query = query.filter(Alert.created_at >= datetime.combine(start_date, datetime.min.time()))
    if end_date:
        query = query.filter(Alert.created_at <= datetime.combine(end_date, datetime.max.time()))

    alerts = query.order_by(Alert.created_at.desc()).all()

    return {
        "building_id": building_id,
        "start_date": str(start_date) if start_date else None,
        "end_date": str(end_date) if end_date else None,
        "total": len(alerts),
        "alerts": [
            {
                "id": a.id,
                "device_id": a.device_id,
                "severity": a.severity,
                "status": a.status,
                "metric_name": a.metric_name,
                "triggered_value": a.triggered_value,
                "created_at": a.created_at,
                "resolved_at": a.resolved_at,
            }
            for a in alerts
        ],
    }


@router.get("/device-availability")
def device_availability(
    building_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """FR-5, FR-31: Summarise current device communication state per building."""
    query = db.query(Device.status, func.count(Device.id).label("count"))

    if building_id:
        query = query.filter(Device.building_id == building_id)

    rows = query.filter(Device.is_active == True).group_by(Device.status).all()

    return {
        "building_id": building_id,
        "status_breakdown": {r.status: r.count for r in rows},
    }
