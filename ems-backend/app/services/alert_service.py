from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.alert import Alert
from app.schemas.alert import AlertCreate, AlertUpdate


class AlertService:
    @staticmethod
    async def get_all(db: AsyncSession, device_id: Optional[str] = None) -> list[Alert]:
        query = select(Alert)
        if device_id:
            query = query.where(Alert.device_id == device_id)
        result = await db.execute(query.order_by(Alert.triggered_at.desc()))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(db: AsyncSession, alert_id: str) -> Optional[Alert]:
        result = await db.execute(select(Alert).where(Alert.id == alert_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, payload: AlertCreate) -> Alert:
        alert = Alert(**payload.model_dump())
        db.add(alert)
        await db.commit()
        await db.refresh(alert)
        return alert

    @staticmethod
    async def update(db: AsyncSession, alert_id: str, payload: AlertUpdate) -> Optional[Alert]:
        alert = await AlertService.get_by_id(db, alert_id)
        if not alert:
            return None
        update_data = payload.model_dump(exclude_unset=True)
        if update_data.get("is_resolved") is True and not alert.is_resolved:
            update_data["resolved_at"] = datetime.now(timezone.utc)
        for field, value in update_data.items():
            setattr(alert, field, value)
        await db.commit()
        await db.refresh(alert)
        return alert
