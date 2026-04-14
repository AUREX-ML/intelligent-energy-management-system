from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
from app.database import get_db
from app.models.building import Building

router = APIRouter()


class BuildingCreate(BaseModel):
    name: str
    address: str
    city: str
    timezone: str = "Africa/Nairobi"


class BuildingUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    tariff_structure: Optional[str] = None
    working_schedule: Optional[str] = None
    alert_routing_policy: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/")
def list_buildings(is_active: Optional[bool] = True, db: Session = Depends(get_db)):
    """FR-57: Return all buildings (optionally filter active only)."""
    query = db.query(Building)
    if is_active is not None:
        query = query.filter(Building.is_active == is_active)
    return query.order_by(Building.name).all()


@router.get("/{building_id}")
def get_building(building_id: int, db: Session = Depends(get_db)):
    """FR-57: Return a single building by ID."""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    return building


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_building(payload: BuildingCreate, db: Session = Depends(get_db)):
    """FR-52, FR-57: Register a new building."""
    building = Building(
        name=payload.name,
        address=payload.address,
        city=payload.city,
        timezone=payload.timezone,
    )
    db.add(building)
    db.commit()
    db.refresh(building)
    return building


@router.patch("/{building_id}")
def update_building(building_id: int, payload: BuildingUpdate, db: Session = Depends(get_db)):
    """FR-55, FR-60: Update building metadata and site-specific policies."""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(building, field, value)
    db.commit()
    db.refresh(building)
    return building


@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_building(building_id: int, db: Session = Depends(get_db)):
    """FR-56: Retire a building without deleting historical data (soft delete)."""
    building = db.query(Building).filter(Building.id == building_id).first()
    if not building:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Building not found")
    building.is_active = False
    db.commit()

