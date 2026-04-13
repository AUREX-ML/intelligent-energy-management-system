from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import AlertCreate, AlertRead, AlertUpdate
from app.services.alert_service import AlertService

router = APIRouter()


@router.get("/", response_model=list[AlertRead])
async def list_alerts(device_id: str | None = None, db: AsyncSession = Depends(get_db)):
    return await AlertService.get_all(db, device_id=device_id)


@router.get("/{alert_id}", response_model=AlertRead)
async def get_alert(alert_id: str, db: AsyncSession = Depends(get_db)):
    alert = await AlertService.get_by_id(db, alert_id)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.post("/", response_model=AlertRead, status_code=status.HTTP_201_CREATED)
async def create_alert(payload: AlertCreate, db: AsyncSession = Depends(get_db)):
    return await AlertService.create(db, payload)


@router.patch("/{alert_id}", response_model=AlertRead)
async def update_alert(alert_id: str, payload: AlertUpdate, db: AsyncSession = Depends(get_db)):
    alert = await AlertService.update(db, alert_id, payload)
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert
