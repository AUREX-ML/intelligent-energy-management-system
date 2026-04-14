"""
FR-15: Detect devices that have missed their heartbeat and create alerts.
Run with Celery beat scheduler.
"""
from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.device import Device, DeviceStatus
from app.models.alert import Alert, AlertSeverity, AlertStatus

def check_device_heartbeats():
    db = SessionLocal()
    try:
        devices = db.query(Device).filter(Device.is_active == True).all()
        now = datetime.utcnow()

        for device in devices:
            if not device.last_seen_at:
                continue
            threshold = timedelta(seconds=device.heartbeat_interval_seconds * 3)
            if now - device.last_seen_at > threshold:
                # Mark device as offline
                device.status = DeviceStatus.offline

                # Check if an open comm-fault alert already exists (FR-30: suppress duplicates)
                existing_alert = db.query(Alert).filter(
                    Alert.device_id == device.id,
                    Alert.status == AlertStatus.open,
                    Alert.metric_name == "communication"
                ).first()
                if not existing_alert:
                    alert = Alert(
                        device_id=device.id,
                        building_id=device.building_id,
                        metric_name="communication",
                        triggered_value="no heartbeat",
                        threshold_condition=f"no message for >{device.heartbeat_interval_seconds * 3}s",
                        severity=AlertSeverity.high,
                        status=AlertStatus.open
                    )
                    db.add(alert)

        db.commit()
    finally:
        db.close()