from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import DeviceCreate, DeviceRead, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter()


@router.get("/", response_model=list[DeviceRead])
async def list_devices(db: AsyncSession = Depends(get_db)):
    return await DeviceService.get_all(db)


@router.get("/{device_id}", response_model=DeviceRead)
async def get_device(device_id: str, db: AsyncSession = Depends(get_db)):
    device = await DeviceService.get_by_id(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.post("/", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
async def create_device(payload: DeviceCreate, db: AsyncSession = Depends(get_db)):
    return await DeviceService.create(db, payload)


@router.patch("/{device_id}", response_model=DeviceRead)
async def update_device(device_id: str, payload: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    device = await DeviceService.update(db, device_id, payload)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    return device


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(device_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await DeviceService.delete(db, device_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
