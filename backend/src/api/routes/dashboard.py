"""
Dashboard routes for analytics and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional

from src.database import get_db
from src.models.ct_scan import CTScan, ScanStatus
from src.models.patient import Patient, PatientStatus
from src.models.scanner import Scanner, ScannerStatus
from src.api.middleware.auth_middleware import get_current_user_id

# Router
dashboard_router = APIRouter()
security = HTTPBearer()


# Response schemas
class DashboardMetrics(BaseModel):
    """Dashboard metrics response."""
    total_patients_today: int
    total_scans_today: int
    scans_in_progress: int
    scans_completed_today: int
    scans_pending: int
    avg_turnaround_time_minutes: float
    scanner_utilization: float
    critical_findings_today: int


class ScanStatusCount(BaseModel):
    """Scan status count."""
    status: str
    count: int


class UrgencyDistribution(BaseModel):
    """Urgency level distribution."""
    urgency_level: str
    count: int


class ScannerUtilization(BaseModel):
    """Scanner utilization data."""
    scanner_id: str
    scanner_code: str
    status: str
    today_scans: int
    daily_capacity: int
    utilization_percent: float


@dashboard_router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get dashboard metrics."""
    await get_current_user_id(credentials)

    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total patients registered today
    result = await db.execute(
        select(func.count(Patient.id)).where(Patient.registered_at >= today)
    )
    total_patients_today = result.scalar() or 0

    # Total scans today
    result = await db.execute(
        select(func.count(CTScan.id)).where(CTScan.ordered_at >= today)
    )
    total_scans_today = result.scalar() or 0

    # Scans in progress
    result = await db.execute(
        select(func.count(CTScan.id)).where(CTScan.status == ScanStatus.IN_PROGRESS)
    )
    scans_in_progress = result.scalar() or 0

    # Scans completed today
    result = await db.execute(
        select(func.count(CTScan.id)).where(
            CTScan.completed_time >= today
        )
    )
    scans_completed_today = result.scalar() or 0

    # Scans pending (ordered or validated)
    result = await db.execute(
        select(func.count(CTScan.id)).where(
            CTScan.status.in_([ScanStatus.ORDERED, ScanStatus.VALIDATED, ScanStatus.SCHEDULED])
        )
    )
    scans_pending = result.scalar() or 0

    # Calculate average turnaround time (completed scans in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    result = await db.execute(
        select(CTScan).where(
            CTScan.completed_time >= week_ago,
            CTScan.completed_time.isnot(None),
        )
    )
    completed_scans = result.scalars().all()

    if completed_scans:
        total_tat = sum(
            (s.completed_time - s.ordered_at).total_seconds() / 60
            for s in completed_scans
            if s.completed_time and s.ordered_at
        )
        avg_turnaround_time_minutes = total_tat / len(completed_scans)
    else:
        avg_turnaround_time_minutes = 0

    # Scanner utilization
    result = await db.execute(select(Scanner).where(Scanner.is_active == True))
    scanners = result.scalars().all()

    if scanners:
        total_capacity = sum(s.daily_capacity for s in scanners)
        total_scans = sum(s.today_scans_completed for s in scanners)
        scanner_utilization = (total_scans / total_capacity * 100) if total_capacity > 0 else 0
    else:
        scanner_utilization = 0

    # Critical findings today
    result = await db.execute(
        select(func.count(CTScan.id)).where(
            CTScan.critical_findings == True,
            CTScan.completed_time >= today,
        )
    )
    critical_findings_today = result.scalar() or 0

    return DashboardMetrics(
        total_patients_today=total_patients_today,
        total_scans_today=total_scans_today,
        scans_in_progress=scans_in_progress,
        scans_completed_today=scans_completed_today,
        scans_pending=scans_pending,
        avg_turnaround_time_minutes=round(avg_turnaround_time_minutes, 1),
        scanner_utilization=round(scanner_utilization, 1),
        critical_findings_today=critical_findings_today,
    )


@dashboard_router.get("/scan-status", response_model=list[ScanStatusCount])
async def get_scan_status_distribution(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get scan status distribution."""
    await get_current_user_id(credentials)

    result = await db.execute(
        select(CTScan.status, func.count(CTScan.id)).group_by(CTScan.status)
    )
    status_counts = result.all()

    return [
        ScanStatusCount(status=status.value, count=count)
        for status, count in status_counts
    ]


@dashboard_router.get("/urgency-distribution", response_model=list[UrgencyDistribution])
async def get_urgency_distribution(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get urgency level distribution."""
    await get_current_user_id(credentials)

    result = await db.execute(
        select(CTScan.urgency_level, func.count(CTScan.id))
        .where(CTScan.status.in_([ScanStatus.ORDERED, ScanStatus.VALIDATED, ScanStatus.SCHEDULED]))
        .group_by(CTScan.urgency_level)
    )
    urgency_counts = result.all()

    return [
        UrgencyDistribution(urgency_level=urgency.value, count=count)
        for urgency, count in urgency_counts
    ]


@dashboard_router.get("/scanner-utilization", response_model=list[ScannerUtilization])
async def get_scanner_utilization(
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get scanner utilization data."""
    await get_current_user_id(credentials)

    result = await db.execute(select(Scanner).where(Scanner.is_active == True))
    scanners = result.scalars().all()

    return [
        ScannerUtilization(
            scanner_id=s.id,
            scanner_code=s.scanner_code,
            status=s.status.value,
            today_scans=s.today_scans_completed,
            daily_capacity=s.daily_capacity,
            utilization_percent=round(
                (s.today_scans_completed / s.daily_capacity * 100) if s.daily_capacity > 0 else 0,
                1
            ),
        )
        for s in scanners
    ]


@dashboard_router.get("/recent-scans", response_model=list[dict])
async def get_recent_scans(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """Get recent scans."""
    await get_current_user_id(credentials)

    result = await db.execute(
        select(CTScan)
        .order_by(CTScan.ordered_at.desc())
        .limit(limit)
    )
    scans = result.scalars().all()

    return [
        {
            "id": s.id,
            "scan_number": s.scan_number,
            "patient_id": s.patient_id,
            "urgency_level": s.urgency_level.value,
            "status": s.status.value,
            "ordered_at": s.ordered_at.isoformat(),
            "completed_time": s.completed_time.isoformat() if s.completed_time else None,
        }
        for s in scans
    ]