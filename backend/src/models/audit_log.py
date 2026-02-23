"""
Audit log model for tracking system activities
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.database import Base


class AuditAction(str, enum.Enum):
    """Audit action types."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    CONSENT = "consent"
    SCAN_START = "scan_start"
    SCAN_COMPLETE = "scan_complete"
    REPORT_GENERATED = "report_generated"
    NOTIFICATION_SENT = "notification_sent"
    ESCALATION = "escalation"


class AuditLog(Base):
    """Audit log model for compliance and tracking."""

    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User who performed the action
    user_id = Column(String(36), ForeignKey("users.id"), index=True)

    # Action details
    action = Column(SQLEnum(AuditAction), nullable=False, index=True)
    entity_type = Column(String(50), index=True)  # e.g., "patient", "scan", "user"
    entity_id = Column(String(36), index=True)

    # Changes (for updates)
    old_values = Column(Text)  # JSON string of old values
    new_values = Column(Text)  # JSON string of new values

    # Additional context
    description = Column(Text)
    ip_address = Column(String(50))
    user_agent = Column(String(500))

    # Outcome
    success = Column(Integer, default=1)  # 1 = success, 0 = failure
    error_message = Column(Text)

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action.value} by {self.user_id} at {self.created_at}>"