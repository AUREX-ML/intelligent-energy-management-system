"""
FR-8: Ingest telemetry via MQTT.
Run this as a separate process: python -m app.services.mqtt_subscriber
"""
import json
import logging
from datetime import datetime
import paho.mqtt.client as mqtt
from app.config import settings
from app.database import SessionLocal
from app.models.device import Device
from app.models.telemetry import TelemetryRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mqtt_subscriber")

TOPIC = "ems/+/telemetry"   # Wildcard: ems/{device_identifier}/telemetry

def on_connect(client, userdata, flags, rc):
    logger.info(f"Connected to MQTT broker (rc={rc})")
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    db = SessionLocal()
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        device_identifier = msg.topic.split("/")[1]

        # FR-9: Validate required fields
        required = ["metric_name", "value", "unit", "timestamp"]
        if not all(k in payload for k in required):
            logger.warning(f"Malformed payload from {device_identifier}: {payload}")
            return

        device = db.query(Device).filter(
            Device.device_identifier == device_identifier,
            Device.is_active == True
        ).first()
        if not device:
            logger.warning(f"Unknown device: {device_identifier}")
            return

        source_ts = datetime.fromisoformat(payload["timestamp"])

        # FR-12: Deduplication
        exists = db.query(TelemetryRecord).filter(
            TelemetryRecord.device_id == device.id,
            TelemetryRecord.metric_name == payload["metric_name"],
            TelemetryRecord.source_timestamp == source_ts
        ).first()
        if exists:
            return

        record = TelemetryRecord(
            device_id=device.id,
            metric_name=payload["metric_name"],
            value=float(payload["value"]),
            unit=payload["unit"],
            source_timestamp=source_ts,
            is_valid=True,
            quality_flag="good"
        )
        db.add(record)
        device.last_seen_at = datetime.utcnow()
        device.status = "online"
        db.commit()
        logger.info(f"Stored: {device_identifier} | {payload['metric_name']} = {payload['value']}")

    except Exception as e:
        logger.error(f"Error processing message: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)
    client.loop_forever()