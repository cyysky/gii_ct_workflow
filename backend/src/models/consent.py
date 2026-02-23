"""
Consent model for digital consent tracking
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey
from datetime import datetime
import uuid
import enum

from src.database import Base


class ConsentType(str, enum.Enum):
    """Type of consent."""
    CT_SCAN = "ct_scan"
    CONTRAST = "contrast"
    SEDATION = "sedation"
    RESEARCH = "research"


class ConsentStatus(str, enum.Enum):
    """Consent status."""
    PENDING = "pending"
    SIGNED = "signed"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"


class Consent(Base):
    """Consent model for digital consent management."""

    __tablename__ = "consents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Link to patient
    patient_id = Column(String(36), ForeignKey("patients.id"), nullable=False, index=True)

    # Consent type
    consent_type = Column(SQLEnum(ConsentType), nullable=False)

    # Status
    status = Column(SQLEnum(ConsentStatus), default=ConsentStatus.PENDING)

    # Consent content
    consent_text = Column(Text, nullable=False)  # Full consent form text
    explanation_provided = Column(Boolean, default=False)  # Was verbal explanation given?

    # Signature
    signature_data = Column(Text)  # Base64 encoded signature or digital signature
    signed_at = Column(DateTime)
    signed_ip = Column(String(50))

    # Witness (for paper consent backup)
    witness_name = Column(String(255))
    witness_id = Column(String(36), ForeignKey("users.id"))

    # Withdrawal
    withdrawn_at = Column(DateTime)
    withdrawal_reason = Column(Text)

    # Metadata
    version = Column(String(20), default="1.0")  # Consent form version
    language = Column(String(10), default="en")

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Consent {self.consent_type.value} - {self.status.value}>"