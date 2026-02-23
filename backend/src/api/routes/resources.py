"""
Resource routes for scanner and capacity management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from src.database import get_db
from src.models.scanner import Scanner, ScannerStatus, ScannerType
from src.api.middleware.auth_middleware import get_current_user_id

# Router
resources_router = APIRouter()
security = HTTPBearer()


# Pydantic schemas
class ScannerCreate(BaseModel):
    """Scanner creation schema."""
    scanner_code: str
    name: str
    location: Optional[str] = None
    scanner_type: ScannerType = ScannerType.STANDARD
    slice_count: Optional[int] = None
    manufacturer: Optional[str] = None
    model: Optional[str] = None
    serial_number: Optional[str] = None
    operational_hours_start: str = "08:00"
    operational_hours_end: str = "22:00"
    avg_scan_duration_minutes: int = 30
    daily_capacity: int = 40


class ScannerUpdate(BaseModel):
    """Scanner update schema."""
    name: Optional[str] = None
    location: Optional[str] = None
    scanner_type: Optional[ScannerType] = None
    slice_count: Optional[int] = None
    status: Optional[ScannerStatus] = None
    operational_hours_start: Optional[str] = None
    operational_hours_end: Optional[str] = None
    avg_scan_duration_minutes: Optional[int] = None
    daily_capacity: Optional[int] = None
    is_active: Optional[bool] = None
    maintenance_notes: Optional[str] = None


class ScannerResponse(BaseModel):
    """Scanner response schema."""
    id: str
    scanner_code: str
    name: str
    location: Optional[str]
    scanner_type: str
    slice_count: Optional[int]
    manufacturer: Optional[str]
    model: Optional[str]
    status: str
    operational_hours_start: str
    operational_hours_end: str
    avg_scan_duration_minutes: int
    daily_capacity: int
    today_scans_completed: int
    today_scans_scheduled: int
    current_utilization: float
    is_active: bool
    created_at: str


def scanner_to_response(scanner: Scanner) -> ScannerResponse:
    """Convert scanner model to response."""
    return ScannerResponse(
        id=scanner.id,
        scanner_code=scanner.scanner_code,
        name=scanner.name,
        location=scanner.location,
        scanner_type=scanner.scanner_type.value,
        slice_count=scanner.slice_count,
        manufacturer=scanner.manufacturer,
        model=scanner.model,
        status=scanner.status.value,
        operational_hours_start=scanner.operational_hours_start,
        operational_hours_end=scanner.operational_hours_end,
        avg_scan_duration_minutes=scanner.avg_scan_duration_minutes,
        daily_capacity=scanner.daily_capacity,
        today_scans_completed=scanner.today_scans_completed,
        today_scans_scheduled=scanner.today_scans_scheduled,
        current_utilization=scanner.current_utilization,
        is_active=scanner.is_active,
        created_at=scanner.created_at.isoformat(),
    )


@resources_router.post("/scanners", response_model=ScannerResponse, status_code=status.HTTP_201_CREATED)
async def create_scanner(
    scanner_data: ScannerCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Create a new CT scanner."""
    await get_current_user_id(credentials)

    # Check if scanner code already exists
    result = await db.execute(select(Scanner).where(Scanner.scanner_code == scanner_data.scanner_code))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Scanner code already exists",
        )

    new_scanner = Scanner(**scanner_data.model_dump())
    db.add(new_scanner)
    await db.commit()
    await db.refresh(new_scanner)

    return scanner_to_response(new_scanner)


@resources_router.get("/scanners", response_model=list[ScannerResponse])
async def list_scanners(
    status: Optional[ScannerStatus] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """List CT scanners with optional filtering."""
    await get_current_user_id(credentials)

    query = select(Scanner)
    if status:
        query = query.where(Scanner.status == status)
    if is_active is not None:
        query = query.where(Scanner.is_active == is_active)

    result = await db.execute(query)
    scanners = result.scalars().all()

    return [scanner_to_response(s) for s in scanners]


@resources_router.get("/scanners/available", response_model=list[ScannerResponse])
async def list_available_scanners(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """List available CT scanners."""
    await get_current_user_id(credentials)

    result = await db.execute(
        select(Scanner).where(
            Scanner.status == ScannerStatus.AVAILABLE,
            Scanner.is_active == True,
        )
    )
    scanners = result.scalars().all()

    return [scanner_to_response(s) for s in scanners]


@resources_router.get("/scanners/{scanner_id}", response_model=ScannerResponse)
async def get_scanner(
    scanner_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get scanner by ID."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Scanner).where(Scanner.id == scanner_id))
    scanner = result.scalar_one_or_none()

    if not scanner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scanner not found",
        )

    return scanner_to_response(scanner)


@resources_router.put("/scanners/{scanner_id}", response_model=ScannerResponse)
async def update_scanner(
    scanner_id: str,
    scanner_data: ScannerUpdate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update scanner information."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Scanner).where(Scanner.id == scanner_id))
    scanner = result.scalar_one_or_none()

    if not scanner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scanner not found",
        )

    update_data = scanner_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scanner, field, value)

    scanner.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(scanner)

    return scanner_to_response(scanner)


@resources_router.patch("/scanners/{scanner_id}/status", response_model=ScannerResponse)
async def update_scanner_status(
    scanner_id: str,
    new_status: ScannerStatus,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update scanner status."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Scanner).where(Scanner.id == scanner_id))
    scanner = result.scalar_one_or_none()

    if not scanner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scanner not found",
        )

    scanner.status = new_status
    scanner.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(scanner)

    return scanner_to_response(scanner)