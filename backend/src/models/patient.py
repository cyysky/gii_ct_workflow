"""
Patient model for ED CT Brain Workflow
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.database import Base


class Gender(str, enum.Enum):
    """Patient gender."""
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class PatientStatus(str, enum.Enum):
    """Patient workflow status."""
    REGISTERED = "registered"
    WAITING = "waiting"
    IN_PREP = "in_prep"
    IN_SCAN = "in_scan"
    POST_SCAN = "post_scan"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AnxietyLevel(str, enum.Enum):
    """Patient anxiety assessment level."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class Patient(Base):
    """Patient model for CT Brain workflow."""

    __tablename__ = "patients"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    mrn = Column(String(50), unique=True, index=True, nullable=False)  # Medical Record Number
    name = Column(String(255), nullable=False)
    ic_number = Column(String(20), unique=True, index=True)  # IC Number (Malaysia)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    phone = Column(String(20))
    email = Column(String(255))
    address = Column(Text)

    # Emergency Department info
    ed_visit_id = Column(String(50), index=True)  # ED Visit ID
    ward = Column(String(100))
    bed_number = Column(String(20))

    # Clinical info
    chief_complaint = Column(Text)
    clinical_notes = Column(Text)
    allergies = Column(Text)

    # Status tracking
    status = Column(SQLEnum(PatientStatus), default=PatientStatus.REGISTERED)
    anxiety_level = Column(SQLEnum(AnxietyLevel), default=AnxietyLevel.NONE)

    # Consent
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime)
    digital_consent_form = Column(Text)

    # Timestamps
    registered_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scans = relationship("CTScan", back_populates="patient")
    notifications = relationship("Notification", back_populates="patient")

    def __repr__(self):
        return f"<Patient {self.mrn} - {self.name}>"