from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.device import Device, DeviceStatus
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:

    @staticmethod
    def get_all(db: Session, building_id: Optional[int] = None, is_active: Optional[bool] = True) -> list[Device]:
        """FR-14: Return the device registry, optionally filtered by building or active state."""
        query = db.query(Device)
        if building_id is not None:
            query = query.filter(Device.building_id == building_id)
        if is_active is not None:
            query = query.filter(Device.is_active == is_active)
        return query.order_by(Device.device_identifier).all()

    @staticmethod
    def get_by_id(db: Session, device_id: int) -> Optional[Device]:
        return db.query(Device).filter(Device.id == device_id).first()

    @staticmethod
    def get_by_identifier(db: Session, device_identifier: str) -> Optional[Device]:
        """FR-14: Look up device by its unique identifier."""
        return db.query(Device).filter(Device.device_identifier == device_identifier).first()

    @staticmethod
    def create(db: Session, payload: DeviceCreate) -> Device:
        """
        FR-52: Register a device with identifier, type, protocol, site, location, heartbeat interval.
        FR-53: Enforce uniqueness of device_identifier.
        """
        existing = DeviceService.get_by_identifier(db, payload.device_identifier)
        if existing:
            raise ValueError(f"Device identifier '{payload.device_identifier}' already exists")

        device = Device(
            device_identifier=payload.device_identifier,
            device_type=payload.device_type,
            protocol=payload.protocol,
            building_id=payload.building_id,
            location_description=payload.location_description,
            heartbeat_interval_seconds=payload.heartbeat_interval_seconds,
            is_controllable=payload.is_controllable,
            is_safety_critical=payload.is_safety_critical,
            status=DeviceStatus.unknown,
            commissioned_at=datetime.utcnow(),
        )
        db.add(device)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def update(db: Session, device_id: int, payload: DeviceUpdate) -> Optional[Device]:
        """FR-55: Update device metadata (configuration history tracked via audit log elsewhere)."""
        device = DeviceService.get_by_id(db, device_id)
        if not device:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def decommission(db: Session, device_id: int) -> Optional[Device]:
        """FR-56: Retire a device without deleting historical data (soft delete)."""
        device = DeviceService.get_by_id(db, device_id)
        if not device:
            return None
        device.is_active = False
        device.status = DeviceStatus.offline
        db.commit()
        db.refresh(device)
        return device

    @staticmethod
    def check_stale_devices(db: Session) -> list[Device]:
        """
        FR-15: Identify devices that have not reported within their configured heartbeat threshold.
        Returns a list of devices whose status was changed to 'offline'.
        """
        active_devices = db.query(Device).filter(Device.is_active == True).all()
        stale = []
        now = datetime.utcnow()
        for device in active_devices:
            if device.last_seen_at is None:
                continue
            threshold = timedelta(seconds=device.heartbeat_interval_seconds * 3)
            if (now - device.last_seen_at) > threshold and device.status != DeviceStatus.offline:
                device.status = DeviceStatus.offline
                stale.append(device)
        if stale:
            db.commit()
        return stale
