"""
Resource Agent for CT scanner scheduling, capacity management, and resource allocation
"""

from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from src.models.scanner import Scanner, ScannerStatus, ScannerType
from src.models.ct_scan import CTScan, ScanStatus, UrgencyLevel


class ResourceAgent:
    """Resource Agent for managing CT scanner resources and scheduling."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def find_available_scanner(
        self,
        scan_duration_minutes: int = 30,
        preferred_type: Optional[ScannerType] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Find an available scanner that can accommodate the scan.
        """
        # Build query for available scanners
        query = select(Scanner).where(
            and_(
                Scanner.status == ScannerStatus.AVAILABLE,
                Scanner.is_active == True,
            )
        )

        if preferred_type:
            query = query.where(Scanner.scanner_type == preferred_type)

        result = await self.db.execute(query)
        scanners = result.scalars().all()

        # Find scanner with enough capacity
        for scanner in scanners:
            if scanner.today_scans_scheduled < scanner.daily_capacity:
                # Check if scan fits in operational hours
                if self._is_within_operational_hours(scanner, scan_duration_minutes):
                    return self._scanner_to_dict(scanner)

        return None

    def _is_within_operational_hours(
        self, scanner: Scanner, duration_minutes: int
    ) -> bool:
        """Check if scan can fit within operational hours."""
        now = datetime.utcnow()

        # Parse operational hours
        start_hour, start_min = map(int, scanner.operational_hours_start.split(":"))
        end_hour, end_min = map(int, scanner.operational_hours_end.split(":"))

        start_time = now.replace(hour=start_hour, minute=start_min, second=0)
        end_time = now.replace(hour=end_hour, minute=end_min, second=0)

        # Calculate end time of proposed scan
        scan_end = now + timedelta(minutes=duration_minutes)

        return now >= start_time and scan_end <= end_time

    def _scanner_to_dict(self, scanner: Scanner) -> Dict[str, Any]:
        """Convert scanner to dictionary."""
        return {
            "id": scanner.id,
            "scanner_code": scanner.scanner_code,
            "name": scanner.name,
            "location": scanner.location,
            "scanner_type": scanner.scanner_type.value,
            "slice_count": scanner.slice_count,
            "avg_scan_duration_minutes": scanner.avg_scan_duration_minutes,
            "daily_capacity": scanner.daily_capacity,
            "today_scans_completed": scanner.today_scans_completed,
            "today_scans_scheduled": scanner.today_scans_scheduled,
            "current_utilization": scanner.current_utilization,
        }

    async def schedule_scan(
        self,
        scan_id: str,
        scanner_id: str,
        scheduled_time: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Schedule a CT scan on a specific scanner.
        """
        # Get scan and scanner
        scan_result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = scan_result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        scanner_result = await self.db.execute(
            select(Scanner).where(Scanner.id == scanner_id)
        )
        scanner = scanner_result.scalar_one_or_none()

        if not scanner:
            raise ValueError("Scanner not found")

        if scanner.status != ScannerStatus.AVAILABLE:
            raise ValueError("Scanner is not available")

        # Schedule the scan
        if scheduled_time is None:
            scheduled_time = datetime.utcnow() + timedelta(minutes=15)

        scan.scanner_id = scanner_id
        scan.scheduled_time = scheduled_time
        scan.status = ScanStatus.SCHEDULED

        # Update scanner capacity
        scanner.today_scans_scheduled += 1

        await self.db.commit()
        await self.db.refresh(scan)
        await self.db.refresh(scanner)

        return {
            "scan_id": scan.id,
            "scanner_id": scanner.id,
            "scanner_code": scanner.scanner_code,
            "scheduled_time": scheduled_time.isoformat(),
            "estimated_duration_minutes": scanner.avg_scan_duration_minutes,
            "estimated_completion": (
                scheduled_time + timedelta(minutes=scanner.avg_scan_duration_minutes)
            ).isoformat(),
        }

    async def get_optimal_schedule(
        self,
        scan_id: str,
        num_suggestions: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Get optimal schedule suggestions for a scan.
        """
        # Get the scan
        scan_result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = scan_result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        # Get all available scanners
        result = await self.db.execute(
            select(Scanner).where(
                and_(
                    Scanner.status == ScannerStatus.AVAILABLE,
                    Scanner.is_active == True,
                )
            )
        )
        scanners = result.scalars().all()

        suggestions = []

        for scanner in scanners:
            if scanner.daily_capacity <= scanner.today_scans_scheduled:
                continue

            # Calculate next available slot
            next_slot = await self._calculate_next_slot(scanner)

            # Adjust for urgency
            if scan.urgency_level == UrgencyLevel.IMMEDIATE:
                next_slot = datetime.utcnow()
            elif scan.urgency_level == UrgencyLevel.URGENT:
                next_slot = min(next_slot, datetime.utcnow() + timedelta(minutes=30))

            suggestions.append({
                "scanner_id": scanner.id,
                "scanner_code": scanner.scanner_code,
                "location": scanner.location,
                "scheduled_time": next_slot.isoformat(),
                "estimated_wait_minutes": max(
                    0, (next_slot - datetime.utcnow()).total_seconds() / 60
                ),
                "estimated_completion": (
                    next_slot + timedelta(minutes=scanner.avg_scan_duration_minutes)
                ).isoformat(),
                "current_utilization": round(
                    (scanner.today_scans_scheduled / scanner.daily_capacity * 100)
                    if scanner.daily_capacity > 0
                    else 0,
                    1,
                ),
            })

        # Sort by scheduled time
        suggestions.sort(key=lambda x: x["scheduled_time"])

        return suggestions[:num_suggestions]

    async def _calculate_next_slot(self, scanner: Scanner) -> datetime:
        """Calculate next available slot on scanner."""
        now = datetime.utcnow()

        # Get scans scheduled for today
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        result = await self.db.execute(
            select(CTScan).where(
                and_(
                    CTScan.scanner_id == scanner.id,
                    CTScan.scheduled_time >= today_start,
                    CTScan.scheduled_time <= today_end,
                    CTScan.status.in_([
                        ScanStatus.SCHEDULED,
                        ScanStatus.IN_PREP,
                        ScanStatus.IN_PROGRESS,
                    ]),
                )
            )
        )
        scheduled_scans = result.scalars().all()

        if not scheduled_scans:
            # No scans today, start from now
            return now + timedelta(minutes=15)

        # Find the last scheduled slot
        last_scan = max(scheduled_scans, key=lambda s: s.scheduled_time or now)

        if last_scan.scheduled_time:
            # Estimate completion time based on average duration
            return last_scan.scheduled_time + timedelta(
                minutes=scanner.avg_scan_duration_minutes
            )

        return now + timedelta(minutes=15)

    async def get_scanner_utilization_report(self) -> Dict[str, Any]:
        """Get utilization report for all scanners."""
        result = await self.db.execute(
            select(Scanner).where(Scanner.is_active == True)
        )
        scanners = result.scalars().all()

        scanner_data = []
        total_capacity = 0
        total_scans = 0

        for scanner in scanners:
            utilization = (
                (scanner.today_scans_completed / scanner.daily_capacity * 100)
                if scanner.daily_capacity > 0
                else 0
            )

            scanner_data.append({
                "scanner_id": scanner.id,
                "scanner_code": scanner.scanner_code,
                "name": scanner.name,
                "status": scanner.status.value,
                "today_scans_completed": scanner.today_scans_completed,
                "today_scans_scheduled": scanner.today_scans_scheduled,
                "daily_capacity": scanner.daily_capacity,
                "utilization_percent": round(utilization, 1),
            })

            total_capacity += scanner.daily_capacity
            total_scans += scanner.today_scans_completed

        overall_utilization = (
            (total_scans / total_capacity * 100) if total_capacity > 0 else 0
        )

        return {
            "scanners": scanner_data,
            "summary": {
                "total_scanners": len(scanners),
                "available_scanners": sum(
                    1 for s in scanner_data if s["status"] == "available"
                ),
                "total_capacity_today": total_capacity,
                "total_scans_completed_today": total_scans,
                "overall_utilization_percent": round(overall_utilization, 1),
            },
        }

    async def forecast_capacity(
        self,
        hours_ahead: int = 24,
    ) -> Dict[str, Any]:
        """
        Forecast capacity for the next N hours.
        """
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours_ahead)

        # Get all scheduled scans in the forecast period
        result = await self.db.execute(
            select(CTScan).where(
                and_(
                    CTScan.scheduled_time >= now,
                    CTScan.scheduled_time <= end_time,
                    CTScan.status.in_([
                        ScanStatus.SCHEDULED,
                        ScanStatus.IN_PREP,
                        ScanStatus.IN_PROGRESS,
                    ]),
                )
            )
        )
        scheduled_scans = result.scalars().all()

        # Get all scanners
        scanners_result = await self.db.execute(
            select(Scanner).where(Scanner.is_active == True)
        )
        scanners = scanners_result.scalars().all()

        # Create hourly breakdown
        hourly_demand = {}
        for scan in scheduled_scans:
            if scan.scheduled_time:
                hour_key = scan.scheduled_time.strftime("%Y-%m-%d %H:00")
                hourly_demand[hour_key] = hourly_demand.get(hour_key, 0) + 1

        # Calculate capacity per hour (assuming 2 scans per hour per scanner average)
        total_scanners = len(scanners)
        capacity_per_hour = total_scanners * 2  # Rough estimate

        forecast = []
        for hour in range(hours_ahead):
            hour_time = now + timedelta(hours=hour)
            hour_key = hour_time.strftime("%Y-%m-%d %H:00")

            demand = hourly_demand.get(hour_key, 0)
            utilization = (demand / capacity_per_hour * 100) if capacity_per_hour > 0 else 0

            forecast.append({
                "hour": hour_key,
                "demand": demand,
                "capacity": capacity_per_hour,
                "utilization_percent": round(utilization, 1),
                "status": "high" if utilization > 80 else "normal" if utilization > 50 else "low",
            })

        return {
            "forecast_period_hours": hours_ahead,
            "hourly_forecast": forecast,
            "recommendations": self._get_capacity_recommendations(forecast),
        }

    def _get_capacity_recommendations(self, forecast: List[Dict]) -> List[str]:
        """Generate capacity recommendations based on forecast."""
        recommendations = []

        high_utilization_hours = [
            f for f in forecast if f["utilization_percent"] > 80
        ]

        if high_utilization_hours:
            hours_str = ", ".join([f["hour"] for f in high_utilization_hours[:3]])
            recommendations.append(
                f"High utilization expected during: {hours_str}"
            )
            recommendations.append(
                "Consider adding extra scanning slots or staff"
            )

        # Check for potential bottlenecks
        if any(f["status"] == "high" for f in forecast):
            recommendations.append(
                "Recommend scheduling non-urgent scans during low-utilization hours"
            )

        return recommendations

    async def update_scanner_status(
        self,
        scanner_id: str,
        new_status: ScannerStatus,
    ) -> Dict[str, Any]:
        """Update scanner status."""
        result = await self.db.execute(
            select(Scanner).where(Scanner.id == scanner_id)
        )
        scanner = result.scalar_one_or_none()

        if not scanner:
            raise ValueError("Scanner not found")

        old_status = scanner.status
        scanner.status = new_status

        await self.db.commit()
        await self.db.refresh(scanner)

        return {
            "scanner_id": scanner.id,
            "scanner_code": scanner.scanner_code,
            "old_status": old_status.value,
            "new_status": new_status.value,
        }