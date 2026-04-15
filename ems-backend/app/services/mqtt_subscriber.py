"""
FR-8: Ingest telemetry via MQTT.
Run this as a separate process: python -m app.services.mqtt_subscriber
"""
import json                          # Used to parse JSON-formatted messages from devices
import logging                       # Used to print informational and error messages to the console
from datetime import datetime        # Used to work with date/time values (e.g. timestamps)
import paho.mqtt.client as mqtt      # The MQTT client library — handles connecting and receiving messages
from app.config import settings      # App-wide settings like broker host/port (loaded from .env)
from app.database import SessionLocal  # Factory that creates a new database session for each message
from app.models.device import Device            # ORM model representing a registered device in the DB
from app.models.telemetry import TelemetryRecord  # ORM model for storing a single telemetry reading

# Configure the logging system to show INFO-level messages and above
logging.basicConfig(level=logging.INFO)
# Create a named logger so log output is clearly labelled "mqtt_subscriber"
logger = logging.getLogger("mqtt_subscriber")

# The MQTT topic pattern this subscriber listens to.
# The '+' is a single-level wildcard, so this matches topics like:
#   ems/device-001/telemetry
#   ems/sensor-abc/telemetry
# The device identifier is always the middle segment.
TOPIC = "ems/+/telemetry"   # Wildcard: ems/{device_identifier}/telemetry

def on_connect(client, userdata, flags, rc):
    # 'rc' is the connection result code — 0 means success, anything else is an error
    logger.info(f"Connected to MQTT broker (rc={rc})")
    # Subscribe to the wildcard topic so we receive messages from all devices
    client.subscribe(TOPIC)

def on_message(client, userdata, msg):
    # Open a new database session; each message gets its own session to keep things isolated
    db = SessionLocal()
    try:
        # msg.payload is raw bytes — decode to a UTF-8 string, then parse as JSON
        payload = json.loads(msg.payload.decode("utf-8"))

        # The topic looks like "ems/device-001/telemetry", so split by "/" and take index 1
        device_identifier = msg.topic.split("/")[1]

        # FR-9: Validate required fields
        # Make sure the incoming message contains every field we need before doing anything else
        required = ["metric_name", "value", "unit", "timestamp"]
        if not all(k in payload for k in required):
            # Log a warning and bail out early — no point continuing with incomplete data
            logger.warning(f"Malformed payload from {device_identifier}: {payload}")
            return

        # Look up the device in the database using its identifier
        # We also check is_active so we ignore decommissioned devices
        device = db.query(Device).filter(
            Device.device_identifier == device_identifier,
            Device.is_active == True
        ).first()
        if not device:
            # If the device isn't registered in our system, skip the message
            logger.warning(f"Unknown device: {device_identifier}")
            return

        # Convert the ISO 8601 timestamp string (e.g. "2026-04-15T10:00:00") into a Python datetime object
        source_ts = datetime.fromisoformat(payload["timestamp"])

        # FR-12: Deduplication
        # Check whether we've already stored a record for this exact device + metric + timestamp.
        # This prevents duplicate entries if the device sends the same reading more than once.
        exists = db.query(TelemetryRecord).filter(
            TelemetryRecord.device_id == device.id,
            TelemetryRecord.metric_name == payload["metric_name"],
            TelemetryRecord.source_timestamp == source_ts
        ).first()
        if exists:
            # Duplicate detected — silently skip without storing or logging (expected behaviour)
            return

        # Build a new TelemetryRecord object with the data from the incoming message
        record = TelemetryRecord(
            device_id=device.id,                      # Foreign key linking to the Device row
            metric_name=payload["metric_name"],        # e.g. "temperature", "power_kw"
            value=float(payload["value"]),             # Cast to float in case it arrived as a string
            unit=payload["unit"],                      # e.g. "°C", "kWh"
            source_timestamp=source_ts,               # The time the device took this reading
            is_valid=True,                             # Mark as valid since it passed all checks above
            quality_flag="good"                        # Indicates the data quality level
        )
        db.add(record)  # Stage the new record to be inserted into the database

        # Update the device's heartbeat fields so the dashboard knows it is still online
        device.last_seen_at = datetime.utcnow()  # Record the current server time as "last seen"
        device.status = "online"                 # Mark the device as active/online

        # Commit both the new telemetry record and the updated device status in one transaction
        db.commit()
        logger.info(f"Stored: {device_identifier} | {payload['metric_name']} = {payload['value']}")

    except Exception as e:
        # Catch-all for unexpected errors (bad JSON, DB errors, etc.) so the subscriber keeps running
        logger.error(f"Error processing message: {e}")
    finally:
        # Always close the DB session when we're done — even if an error occurred above
        db.close()

if __name__ == "__main__":
    # Create an MQTT client instance using the V1 callback API
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)

    # Register the callback functions defined above
    client.on_connect = on_connect  # Called once the broker accepts the connection
    client.on_message = on_message  # Called every time a new message arrives on a subscribed topic

    # Connect to the broker using host/port from settings (e.g. "localhost", 1883)
    # keepalive=60 means the client sends a ping every 60 seconds to keep the connection alive
    client.connect(settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT, keepalive=60)

    # Start a blocking loop that listens for incoming messages indefinitely
    # Press Ctrl+C to stop the process
    client.loop_forever()