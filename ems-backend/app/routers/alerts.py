from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.alert import Alert, AlertStatus

router = APIRouter()

@router.get("/")
def list_alerts(building_id: int = None, status: str = None, db: Session = Depends(get_db)):
    """FR-28: Return alerts filtered by building and/or status."""
    query = db.query(Alert)
    if building_id:
        query = query.filter(Alert.building_id == building_id)
    if status:
        query = query.filter(Alert.status == status)
    return query.order_by(Alert.created_at.desc()).limit(200).all()

@router.patch("/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, db: Session = Depends(get_db)):
    """FR-28: Acknowledge an open alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.acknowledged
    alert.acknowledged_at = datetime.utcnow()
    db.commit()
    return {"status": "acknowledged", "alert_id": alert_id}

@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int, notes: str = "", db: Session = Depends(get_db)):
    """FR-28, FR-29: Resolve alert with notes."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    alert.status = AlertStatus.resolved
    alert.resolved_at = datetime.utcnow()
    alert.resolution_notes = notes
    db.commit()
    return {"status": "resolved", "alert_id": alert_id}
