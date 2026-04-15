"""
FR-15: Detect devices that have missed their heartbeat and create alerts.
Run with Celery beat scheduler.
"""
from datetime import datetime, timedelta  # datetime: current time; timedelta: represents a duration (e.g. "90 seconds")
from app.database import SessionLocal     # Factory that creates a new database session for this task
from app.models.device import Device, DeviceStatus          # Device row model + its status enum (online/offline/etc.)
from app.models.alert import Alert, AlertSeverity, AlertStatus  # Alert row model + severity/status enums

def check_device_heartbeats():
    # Open a fresh database session for this entire check cycle
    db = SessionLocal()
    try:
        # Fetch every device that is active (not decommissioned) from the database
        devices = db.query(Device).filter(Device.is_active == True).all()

        # Capture the current UTC time once so all comparisons use the exact same moment
        now = datetime.utcnow()

        for device in devices:
            # If the device has never sent a message, last_seen_at will be None.
            # Skip it — we can't calculate a silence duration without a starting point.
            if not device.last_seen_at:
                continue

            # Calculate how long the device is allowed to be silent before we consider it offline.
            # We use 3× the device's own heartbeat interval as a generous tolerance window.
            # For example: if heartbeat_interval_seconds=30, the threshold is 90 seconds.
            threshold = timedelta(seconds=device.heartbeat_interval_seconds * 3)

            # Compare the silence duration (now minus last message time) to the threshold.
            # If the gap is longer than the threshold, the device has missed its heartbeat.
            if now - device.last_seen_at > threshold:
                # Mark device as offline
                # Update the device's status in the database so the dashboard reflects it
                device.status = DeviceStatus.offline

                # Check if an open comm-fault alert already exists (FR-30: suppress duplicates)
                # We only want ONE open alert per device at a time — no need to spam the alerts table.
                existing_alert = db.query(Alert).filter(
                    Alert.device_id == device.id,       # Must belong to this specific device
                    Alert.status == AlertStatus.open,   # Only look at alerts still open (not resolved)
                    Alert.metric_name == "communication"  # Only look at communication-type alerts
                ).first()

                if not existing_alert:
                    # No existing open alert for this device — create a new one
                    alert = Alert(
                        device_id=device.id,            # Link the alert to the affected device
                        building_id=device.building_id, # Also store the building for easy filtering
                        metric_name="communication",    # Category of the alert — a connectivity fault
                        triggered_value="no heartbeat", # Human-readable description of what went wrong
                        # Describe the exact rule that was violated, e.g. "no message for >90s"
                        threshold_condition=f"no message for >{device.heartbeat_interval_seconds * 3}s",
                        severity=AlertSeverity.high,    # Missing heartbeats are treated as high severity
                        status=AlertStatus.open         # Mark the alert as open (needs attention)
                    )
                    db.add(alert)  # Stage the new alert to be saved to the database

        # Persist all device status updates and new alerts in a single transaction
        db.commit()
    finally:
        # Always release the database session, even if an error occurred above
        db.close()