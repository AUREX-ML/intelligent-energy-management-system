from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.device import Device
from app.schemas.device import DeviceCreate, DeviceUpdate


class DeviceService:
    @staticmethod
    async def get_all(db: AsyncSession) -> list[Device]:
        result = await db.execute(select(Device))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, device_id: str) -> Optional[Device]:
        result = await db.execute(select(Device).where(Device.id == device_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, payload: DeviceCreate) -> Device:
        device = Device(**payload.model_dump())
        db.add(device)
        await db.commit()
        await db.refresh(device)
        return device

    @staticmethod
    async def update(db: AsyncSession, device_id: str, payload: DeviceUpdate) -> Optional[Device]:
        device = await DeviceService.get_by_id(db, device_id)
        if not device:
            return None
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(device, field, value)
        await db.commit()
        await db.refresh(device)
        return device

    @staticmethod
    async def delete(db: AsyncSession, device_id: str) -> bool:
        device = await DeviceService.get_by_id(db, device_id)
        if not device:
            return False
        await db.delete(device)
        await db.commit()
        return True
