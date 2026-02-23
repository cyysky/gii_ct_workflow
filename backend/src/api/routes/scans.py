"""
CT Scan routes for managing CT Brain imaging workflow
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid

from src.database import get_db
from src.models.ct_scan import CTScan, ScanStatus, UrgencyLevel, AppropriatenessScore, CTContrast
from src.models.patient import Patient
from src.api.middleware.auth_middleware import get_current_user_id

# Router
scans_router = APIRouter()
security = HTTPBearer()


# Pydantic schemas
class CTScanCreate(BaseModel):
    """CT Scan creation schema."""
    patient_id: str
    ct_indication: str
    clinical_history: Optional[str] = None
    symptoms: Optional[str] = None
    onset_time: Optional[datetime] = None
    gcs_score: Optional[int] = None
    neurological_findings: Optional[str] = None
    urgency_level: UrgencyLevel = UrgencyLevel.ROUTINE
    contrast: CTContrast = CTContrast.WITHOUT_CONTRAST


class CTScanUpdate(BaseModel):
    """CT Scan update schema."""
    ct_indication: Optional[str] = None
    clinical_history: Optional[str] = None
    symptoms: Optional[str] = None
    neurological_findings: Optional[str] = None
    urgency_level: Optional[UrgencyLevel] = None
    contrast: Optional[CTContrast] = None
    status: Optional[ScanStatus] = None
    scanner_id: Optional[str] = None
    scheduled_time: Optional[datetime] = None
    started_time: Optional[datetime] = None
    completed_time: Optional[datetime] = None
    preliminary_report: Optional[str] = None
    final_report: Optional[str] = None
    critical_findings: Optional[bool] = None


class CTScanResponse(BaseModel):
    """CT Scan response schema."""
    id: str
    scan_number: str
    patient_id: str
    ordering_physician_id: Optional[str]
    radiology_technician_id: Optional[str]
    radiologist_id: Optional[str]
    scanner_id: Optional[str]
    ct_indication: str
    clinical_history: Optional[str]
    symptoms: Optional[str]
    onset_time: Optional[datetime]
    gcs_score: Optional[int]
    neurological_findings: Optional[str]
    urgency_level: str
    appropriateness_score: Optional[str]
    contrast: str
    status: str
    scheduled_time: Optional[datetime]
    started_time: Optional[datetime]
    completed_time: Optional[datetime]
    preliminary_report: Optional[str]
    final_report: Optional[str]
    critical_findings: bool
    ordered_at: datetime
    created_at: datetime


def scan_to_response(scan: CTScan) -> CTScanResponse:
    """Convert scan model to response."""
    return CTScanResponse(
        id=scan.id,
        scan_number=scan.scan_number,
        patient_id=scan.patient_id,
        ordering_physician_id=scan.ordering_physician_id,
        radiology_technician_id=scan.radiology_technician_id,
        radiologist_id=scan.radiologist_id,
        scanner_id=scan.scanner_id,
        ct_indication=scan.ct_indication,
        clinical_history=scan.clinical_history,
        symptoms=scan.symptoms,
        onset_time=scan.onset_time,
        gcs_score=scan.gcs_score,
        neurological_findings=scan.neurological_findings,
        urgency_level=scan.urgency_level.value,
        appropriateness_score=scan.appropriateness_score.value if scan.appropriateness_score else None,
        contrast=scan.contrast.value,
        status=scan.status.value,
        scheduled_time=scan.scheduled_time,
        started_time=scan.started_time,
        completed_time=scan.completed_time,
        preliminary_report=scan.preliminary_report,
        final_report=scan.final_report,
        critical_findings=scan.critical_findings,
        ordered_at=scan.ordered_at,
        created_at=scan.created_at,
    )


def generate_scan_number() -> str:
    """Generate a unique scan number."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    return f"CT-{timestamp}-{uuid.uuid4().hex[:4].upper()}"


@scans_router.post("/", response_model=CTScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: CTScanCreate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Create a new CT scan order."""
    user_id = await get_current_user_id(credentials)

    # Verify patient exists
    result = await db.execute(select(Patient).where(Patient.id == scan_data.patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found",
        )

    new_scan = CTScan(
        scan_number=generate_scan_number(),
        ordering_physician_id=user_id,
        **scan_data.model_dump(),
    )

    db.add(new_scan)
    await db.commit()
    await db.refresh(new_scan)

    return scan_to_response(new_scan)


@scans_router.get("/", response_model=list[CTScanResponse])
async def list_scans(
    status: Optional[ScanStatus] = None,
    patient_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """List CT scans with optional filtering."""
    await get_current_user_id(credentials)

    query = select(CTScan)
    if status:
        query = query.where(CTScan.status == status)
    if patient_id:
        query = query.where(CTScan.patient_id == patient_id)

    query = query.offset(skip).limit(limit).order_by(CTScan.ordered_at.desc())
    result = await db.execute(query)
    scans = result.scalars().all()

    return [scan_to_response(s) for s in scans]


@scans_router.get("/{scan_id}", response_model=CTScanResponse)
async def get_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get CT scan by ID."""
    await get_current_user_id(credentials)

    result = await db.execute(select(CTScan).where(CTScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CT scan not found",
        )

    return scan_to_response(scan)


@scans_router.put("/{scan_id}", response_model=CTScanResponse)
async def update_scan(
    scan_id: str,
    scan_data: CTScanUpdate,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update CT scan information."""
    await get_current_user_id(credentials)

    result = await db.execute(select(CTScan).where(CTScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CT scan not found",
        )

    update_data = scan_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scan, field, value)

    scan.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(scan)

    return scan_to_response(scan)


@scans_router.patch("/{scan_id}/status", response_model=CTScanResponse)
async def update_scan_status(
    scan_id: str,
    new_status: ScanStatus,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Update CT scan status."""
    await get_current_user_id(credentials)

    result = await db.execute(select(CTScan).where(CTScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CT scan not found",
        )

    scan.status = new_status

    # Update timestamps based on status
    if new_status == ScanStatus.IN_PROGRESS:
        scan.started_time = datetime.utcnow()
    elif new_status == ScanStatus.COMPLETED:
        scan.completed_time = datetime.utcnow()
    elif new_status == ScanStatus.REPORTED:
        scan.reported_time = datetime.utcnow()

    scan.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(scan)

    return scan_to_response(scan)


@scans_router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(
    scan_id: str,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Delete a CT scan order."""
    await get_current_user_id(credentials)

    result = await db.execute(select(CTScan).where(CTScan.id == scan_id))
    scan = result.scalar_one_or_none()

    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CT scan not found",
        )

    await db.delete(scan)
    await db.commit()

    return None