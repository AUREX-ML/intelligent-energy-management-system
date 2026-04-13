from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import TelemetryCreate, TelemetryRead
from app.services.telemetry_service import TelemetryService

router = APIRouter()


@router.get("/", response_model=list[TelemetryRead])
async def list_telemetry(device_id: str | None = None, db: AsyncSession = Depends(get_db)):
    return await TelemetryService.get_all(db, device_id=device_id)


@router.post("/", response_model=TelemetryRead, status_code=status.HTTP_201_CREATED)
async def ingest_telemetry(payload: TelemetryCreate, db: AsyncSession = Depends(get_db)):
    return await TelemetryService.create(db, payload)
