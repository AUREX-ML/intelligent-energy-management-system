from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.telemetry import Telemetry
from app.schemas.telemetry import TelemetryCreate


class TelemetryService:
    @staticmethod
    async def get_all(db: AsyncSession, device_id: Optional[str] = None) -> list[Telemetry]:
        query = select(Telemetry)
        if device_id:
            query = query.where(Telemetry.device_id == device_id)
        result = await db.execute(query.order_by(Telemetry.recorded_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, payload: TelemetryCreate) -> Telemetry:
        record = Telemetry(**payload.model_dump())
        db.add(record)
        await db.commit()
        await db.refresh(record)
        return record
