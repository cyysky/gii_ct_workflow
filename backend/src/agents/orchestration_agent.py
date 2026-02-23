"""
Orchestration Agent for workflow coordination, task routing, and audit logging
"""

from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import json
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from src.models.ct_scan import CTScan, ScanStatus
from src.models.patient import Patient, PatientStatus
from src.models.user import User, UserRole
from src.models.audit_log import AuditLog, AuditAction
from src.agents.patient_agent import PatientAgent
from src.agents.clinical_agent import ClinicalAgent
from src.agents.resource_agent import ResourceAgent


class WorkflowState:
    """Workflow state tracking."""

    def __init__(self):
        self.current_step: str = ""
        self.completed_steps: List[str] = []
        self.pending_actions: List[str] = []
        self.escalation_level: int = 0
        self.last_updated: datetime = datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_step": self.current_step,
            "completed_steps": self.completed_steps,
            "pending_actions": self.pending_actions,
            "escalation_level": self.escalation_level,
            "last_updated": self.last_updated.isoformat(),
        }


class OrchestrationAgent:
    """
    Orchestration Agent for coordinating the CT Brain workflow.
    Handles task routing, escalation, and audit logging.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.patient_agent = PatientAgent(db)
        self.clinical_agent = ClinicalAgent(db)
        self.resource_agent = ResourceAgent(db)

    async def process_new_scan_order(
        self,
        scan_id: str,
        initiated_by: str,
    ) -> Dict[str, Any]:
        """
        Process a new CT scan order through the workflow.
        """
        workflow = WorkflowState()
        workflow.current_step = "order_received"

        # Log the action
        await self._log_audit(
            user_id=initiated_by,
            action=AuditAction.CREATE,
            entity_type="scan",
            entity_id=scan_id,
            description=f"New CT scan order created",
        )

        # Step 1: Validate clinical indication
        workflow.current_step = "clinical_validation"
        scan_result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = scan_result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        # Run clinical analysis
        clinical_analysis = await self.clinical_agent.analyze_ct_indication(
            ct_indication=scan.ct_indication,
            clinical_history=scan.clinical_history,
            symptoms=scan.symptoms,
        )

        # Update scan with clinical analysis
        scan.urgency_level = clinical_analysis["urgency_level"]
        scan.appropriateness_score = clinical_analysis["appropriateness_score"]
        scan.status = ScanStatus.VALIDATED

        workflow.completed_steps.append("clinical_validation")
        workflow.pending_actions.extend(clinical_analysis.get("recommendations", []))

        await self._log_audit(
            user_id=initiated_by,
            action=AuditAction.UPDATE,
            entity_type="scan",
            entity_id=scan_id,
            description=f"Clinical validation completed: {clinical_analysis['urgency_level']}",
        )

        # Step 2: Schedule the scan
        workflow.current_step = "scheduling"

        if clinical_analysis["urgency_level"] == "immediate":
            # Find immediate scanner
            scanner = await self.resource_agent.find_available_scanner(
                scan_duration_minutes=15  # Emergency scan
            )

            if scanner:
                await self.resource_agent.schedule_scan(
                    scan_id=scan_id,
                    scanner_id=scanner["id"],
                )
                workflow.completed_steps.append("scheduling")
            else:
                # Escalate if no scanner available
                await self._escalate(scan_id, "No scanner available for immediate scan")
        else:
            # Get schedule suggestions
            suggestions = await self.resource_agent.get_optimal_schedule(
                scan_id=scan_id,
                num_suggestions=3,
            )

            if suggestions:
                # Auto-schedule on first available slot
                await self.resource_agent.schedule_scan(
                    scan_id=scan_id,
                    scanner_id=suggestions[0]["scanner_id"],
                )
                workflow.completed_steps.append("scheduling")
            else:
                workflow.pending_actions.append("Awaiting scanner availability")

        # Step 3: Update patient status
        workflow.current_step = "patient_notification"

        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == scan.patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        if patient:
            patient.status = PatientStatus.WAITING

            # Send notification to patient
            try:
                await self.patient_agent.send_notification(
                    patient_id=patient.id,
                    notification_type="in_app",
                    category="appointment",
                    title="CT Scan Scheduled",
                    message=f"Your CT brain scan has been scheduled. Please proceed to the Radiology Department.",
                    related_entity_type="scan",
                    related_entity_id=scan_id,
                )
            except Exception:
                pass  # Continue even if notification fails

            workflow.completed_steps.append("patient_notification")

        # Complete workflow
        workflow.current_step = "completed"

        await self.db.commit()

        return {
            "scan_id": scan_id,
            "workflow_state": workflow.to_dict(),
            "clinical_analysis": clinical_analysis,
        }

    async def update_scan_status(
        self,
        scan_id: str,
        new_status: ScanStatus,
        updated_by: str,
    ) -> Dict[str, Any]:
        """Update scan status and handle workflow transitions."""
        scan_result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = scan_result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        old_status = scan.status
        scan.status = new_status

        # Handle status-specific actions
        if new_status == ScanStatus.IN_PREP:
            # Update patient status
            patient_result = await self.db.execute(
                select(Patient).where(Patient.id == scan.patient_id)
            )
            patient = patient_result.scalar_one_or_none()
            if patient:
                patient.status = PatientStatus.IN_PREP

        elif new_status == ScanStatus.IN_PROGRESS:
            # Start scan timer
            scan.started_time = datetime.utcnow()

            # Update patient status
            patient_result = await self.db.execute(
                select(Patient).where(Patient.id == scan.patient_id)
            )
            patient = patient_result.scalar_one_or_none()
            if patient:
                patient.status = PatientStatus.IN_SCAN

        elif new_status == ScanStatus.COMPLETED:
            # Complete scan
            scan.completed_time = datetime.utcnow()

            # Update scanner utilization
            if scan.scanner_id:
                scanner_result = await self.db.execute(
                    select(Patient).where(Patient.id == scan.scanner_id)
                )

            # Update patient status
            patient_result = await self.db.execute(
                select(Patient).where(Patient.id == scan.patient_id)
            )
            patient = patient_result.scalar_one_or_none()
            if patient:
                patient.status = PatientStatus.POST_SCAN

        elif new_status == ScanStatus.REPORTED:
            # Report generated
            scan.reported_time = datetime.utcnow()

            # Update patient status
            patient_result = await self.db.execute(
                select(Patient).where(Patient.id == scan.patient_id)
            )
            patient = patient_result.scalar_one_or_none()
            if patient:
                patient.status = PatientStatus.COMPLETED

                # Send result notification
                if scan.final_report:
                    try:
                        await self.patient_agent.send_notification(
                            patient_id=patient.id,
                            notification_type="in_app",
                            category="result_ready",
                            title="CT Scan Results Ready",
                            message="Your CT scan results are now available. Please consult your doctor for the report.",
                            related_entity_type="scan",
                            related_entity_id=scan_id,
                        )
                    except Exception:
                        pass

        await self._log_audit(
            user_id=updated_by,
            action=AuditAction.UPDATE,
            entity_type="scan",
            entity_id=scan_id,
            description=f"Scan status changed from {old_status.value} to {new_status.value}",
        )

        await self.db.commit()

        return {
            "scan_id": scan_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "completed_at": scan.completed_time.isoformat() if scan.completed_time else None,
        }

    async def _escalate(self, scan_id: str, reason: str):
        """Escalate workflow issue."""
        await self._log_audit(
            user_id="system",
            action=AuditAction.ESCALATION,
            entity_type="scan",
            entity_id=scan_id,
            description=f"Escalation: {reason}",
        )

        # In production, this would trigger alerts to supervisors
        # and potentially auto-add to emergency scanner queue

    async def _log_audit(
        self,
        user_id: str,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        description: str,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
    ):
        """Log audit event."""
        audit_log = AuditLog(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            description=description,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
        )

        self.db.add(audit_log)
        await self.db.commit()

    async def get_workflow_status(self, scan_id: str) -> Dict[str, Any]:
        """Get current workflow status for a scan."""
        scan_result = await self.db.execute(select(CTScan).where(CTScan.id == scan_id))
        scan = scan_result.scalar_one_or_none()

        if not scan:
            raise ValueError("CT scan not found")

        patient_result = await self.db.execute(
            select(Patient).where(Patient.id == scan.patient_id)
        )
        patient = patient_result.scalar_one_or_none()

        # Build workflow timeline
        timeline = [
            {
                "step": "Order Placed",
                "timestamp": scan.ordered_at.isoformat() if scan.ordered_at else None,
                "completed": True,
            },
            {
                "step": "Clinical Validation",
                "timestamp": None,
                "completed": scan.status in [
                    ScanStatus.VALIDATED,
                    ScanStatus.SCHEDULED,
                    ScanStatus.IN_PREP,
                    ScanStatus.IN_PROGRESS,
                    ScanStatus.COMPLETED,
                    ScanStatus.REPORTED,
                ],
            },
            {
                "step": "Scheduled",
                "timestamp": scan.scheduled_time.isoformat() if scan.scheduled_time else None,
                "completed": scan.status in [
                    ScanStatus.SCHEDULED,
                    ScanStatus.IN_PREP,
                    ScanStatus.IN_PROGRESS,
                    ScanStatus.COMPLETED,
                    ScanStatus.REPORTED,
                ],
            },
            {
                "step": "In Preparation",
                "timestamp": None,
                "completed": scan.status in [
                    ScanStatus.IN_PREP,
                    ScanStatus.IN_PROGRESS,
                    ScanStatus.COMPLETED,
                    ScanStatus.REPORTED,
                ],
            },
            {
                "step": "Scanning",
                "timestamp": scan.started_time.isoformat() if scan.started_time else None,
                "completed": scan.status in [
                    ScanStatus.IN_PROGRESS,
                    ScanStatus.COMPLETED,
                    ScanStatus.REPORTED,
                ],
            },
            {
                "step": "Completed",
                "timestamp": scan.completed_time.isoformat() if scan.completed_time else None,
                "completed": scan.status in [ScanStatus.COMPLETED, ScanStatus.REPORTED],
            },
            {
                "step": "Reported",
                "timestamp": scan.reported_time.isoformat() if scan.reported_time else None,
                "completed": scan.status == ScanStatus.REPORTED,
            },
        ]

        # Calculate TAT if completed
        turnaround_time = None
        if scan.completed_time and scan.ordered_at:
            turnaround_time = (
                (scan.completed_time - scan.ordered_at).total_seconds() / 60
            )

        return {
            "scan_id": scan.id,
            "scan_number": scan.scan_number,
            "patient_id": scan.patient_id,
            "patient_name": patient.name if patient else None,
            "current_status": scan.status.value,
            "urgency_level": scan.urgency_level.value,
            "timeline": timeline,
            "turnaround_time_minutes": (
                round(turnaround_time, 1) if turnaround_time else None
            ),
        }

    async def get_pending_actions(self, user_role: str = None) -> Dict[str, Any]:
        """Get pending actions for the workflow."""
        # Get scans needing attention
        pending_scans = []

        # Scans that need scheduling
        result = await self.db.execute(
            select(CTScan).where(CTScan.status == ScanStatus.VALIDATED)
        )
        validated_scans = result.scalars().all()

        for scan in validated_scans:
            pending_scans.append({
                "scan_id": scan.id,
                "scan_number": scan.scan_number,
                "urgency": scan.urgency_level.value,
                "action_needed": "Schedule scan",
            })

        # Scans that need to start
        result = await self.db.execute(
            select(CTScan).where(CTScan.status == ScanStatus.SCHEDULED)
        )
        scheduled_scans = result.scalars().all()

        now = datetime.utcnow()
        for scan in scheduled_scans:
            if scan.scheduled_time and scan.scheduled_time <= now:
                pending_scans.append({
                    "scan_id": scan.id,
                    "scan_number": scan.scan_number,
                    "urgency": scan.urgency_level.value,
                    "action_needed": "Start scan",
                })

        # Scans needing report
        result = await self.db.execute(
            select(CTScan).where(CTScan.status == ScanStatus.COMPLETED)
        )
        completed_scans = result.scalars().all()

        for scan in completed_scans:
            pending_scans.append({
                "scan_id": scan.id,
                "scan_number": scan.scan_number,
                "urgency": scan.urgency_level.value,
                "action_needed": "Generate report",
            })

        return {
            "pending_actions": pending_scans,
            "total_pending": len(pending_scans),
            "urgent_count": sum(
                1 for s in pending_scans if s["urgency"] == "immediate"
            ),
        }