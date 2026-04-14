from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.schemas.device import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter()


@router.get("/", response_model=list[DeviceRead])
def list_devices(
    building_id: Optional[int] = Query(None, description="Filter by building"),
    is_active: Optional[bool] = Query(True, description="Filter by active state"),
    db: Session = Depends(get_db),
):
    """FR-14: Return the full device registry with optional building/active filters."""
    return DeviceService.get_all(db, building_id=building_id, is_active=is_active)


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: int, db: Session = Depends(get_db)):
    """FR-14: Return a single device by its integer primary key."""
    device = DeviceService.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.post("/", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    """
    FR-52: Register a device with identifier, type, protocol, site, location, heartbeat interval.
    FR-53: Rejects duplicate device_identifier.
    """
    try:
        return DeviceService.create(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{device_id}", response_model=DeviceRead)
def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db)):
    """FR-55: Update device metadata fields."""
    device = DeviceService.update(db, device_id, payload)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.delete("/{device_id}", response_model=DeviceRead)
def decommission_device(device_id: int, db: Session = Depends(get_db)):
    """FR-56: Soft-decommission a device — marks inactive, preserves all historical data."""
    device = DeviceService.decommission(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.get("/{device_id}/connectivity")
def test_connectivity(device_id: int, db: Session = Depends(get_db)):
    """FR-54: Check device connectivity status during or after commissioning."""
    device = DeviceService.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return {
        "device_id": device.id,
        "device_identifier": device.device_identifier,
        "status": device.status,
        "last_seen_at": device.last_seen_at,
        "heartbeat_interval_seconds": device.heartbeat_interval_seconds,
        "is_online": device.status == "online",
    }
