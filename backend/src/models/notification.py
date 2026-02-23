"""
Notification model for patient communication
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.database import Base


class NotificationType(str, enum.Enum):
    """Type of notification."""
    SMS = "sms"
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    IN_APP = "in_app"
    PUSH = "push"


class NotificationStatus(str, enum.Enum):
    """Notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class NotificationCategory(str, enum.Enum):
    """Notification category."""
    APPOINTMENT = "appointment"
    REMINDER = "reminder"
    RESULT_READY = "result_ready"
    STATUS_UPDATE = "status_update"
    FEEDBACK = "feedback"
    GENERAL = "general"


class Notification(Base):
    """Notification model for patient communication."""

    __tablename__ = "notifications"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Recipient
    patient_id = Column(String(36), ForeignKey("patients.id"), index=True)
    recipient_phone = Column(String(20))
    recipient_email = Column(String(255))

    # Notification details
    notification_type = Column(SQLEnum(NotificationType), nullable=False)
    category = Column(SQLEnum(NotificationCategory), nullable=False, index=True)

    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    language = Column(String(10), default="en")

    # Status
    status = Column(SQLEnum(NotificationStatus), default=NotificationStatus.PENDING, index=True)

    # Delivery details
    sent_at = Column(DateTime)
    delivered_at = Column(DateTime)
    read_at = Column(DateTime)

    # External service integration
    external_id = Column(String(100))  # e.g., Twilio message SID
    provider_response = Column(Text)  # Response from SMS/Email provider

    # Related entities
    related_entity_type = Column(String(50))  # e.g., "scan", "consent"
    related_entity_id = Column(String(36))

    # Retry handling
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    last_retry_at = Column(DateTime)
    failure_reason = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    patient = relationship("Patient", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.notification_type.value} - {self.category.value}>"