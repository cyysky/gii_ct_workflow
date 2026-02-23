"""
CT Scan model for tracking CT Brain imaging workflow
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.database import Base


class ScanStatus(str, enum.Enum):
    """CT Scan workflow status."""
    ORDERED = "ordered"
    VALIDATED = "validated"
    SCHEDULED = "scheduled"
    IN_PREP = "in_prep"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REPORTED = "reported"
    CANCELLED = "cancelled"


class UrgencyLevel(str, enum.Enum):
    """Urgency level for CT scan."""
    IMMEDIATE = "immediate"  # Life-threatening, needs immediate scan
    URGENT = "urgent"        # Within 1 hour
    ROUTINE = "routine"     # Within 24 hours


class AppropriatenessScore(str, enum.Enum):
    """CT Appropriateness score based on UCLA criteria."""
    VERY_HIGH = "very_high"   # Score 7-9
    HIGH = "high"            # Score 6
    MODERATE = "moderate"    # Score 4-5
    LOW = "low"              # Score 2-3
    VERY_LOW = "very_low"    # Score 1


class CTContrast(str, enum.Enum):
    """CT Contrast type."""
    NONE = "none"
    WITH_CONTRAST = "with_contrast"
    WITHOUT_CONTRAST = "without_contrast"


class CTScan(Base):
    """CT Scan model for tracking imaging workflow."""

    __tablename__ = "ct_scans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scan_number = Column(String(50), unique=True, index=True, nullable=False)  # Scan Order Number

    # Foreign keys
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)
    ordering_physician_id = Column(String(36), ForeignKey("users.id"))
    radiology_technician_id = Column(String(36), ForeignKey("users.id"))
    radiologist_id = Column(String(36), ForeignKey("users.id"))
    scanner_id = Column(String(36), ForeignKey("scanners.id"), index=True)

    # Clinical information
    ct_indication = Column(Text, nullable=False)  # Reason for CT scan
    clinical_history = Column(Text)
    symptoms = Column(Text)
    onset_time = Column(DateTime)
    gcs_score = Column(Integer)  # Glasgow Coma Scale
    neurological_findings = Column(Text)

    # Urgency and appropriateness
    urgency_level = Column(SQLEnum(UrgencyLevel), default=UrgencyLevel.ROUTINE)
    appropriateness_score = Column(SQLEnum(AppropriatenessScore))
    appropriateness_reason = Column(Text)

    # Scan details
    contrast = Column(SQLEnum(CTContrast), default=CTContrast.WITHOUT_CONTRAST)

    # AI analysis (placeholder for future image analysis)
    ai_preliminary_findings = Column(Text)
    ai_motion_artifact = Column(Boolean, default=False)
    ai_quality_score = Column(Float)  # Image quality score 0-100

    # Status tracking
    status = Column(SQLEnum(ScanStatus), default=ScanStatus.ORDERED)

    # Scheduling
    scheduled_time = Column(DateTime)
    started_time = Column(DateTime)
    completed_time = Column(DateTime)
    reported_time = Column(DateTime)

    # Results
    preliminary_report = Column(Text)
    final_report = Column(Text)
    critical_findings = Column(Boolean, default=False)
    critical_findings_notification = Column(Boolean, default=False)

    # Transport
    transport_requested = Column(Boolean, default=False)
    transport_eta = Column(DateTime)
    transport_team = Column(String(100))

    # Timestamps
    ordered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="scans")
    scanner = relationship("Scanner", back_populates="scans")

    def __repr__(self):
        return f"<CTScan {self.scan_number} - {self.status.value}>"