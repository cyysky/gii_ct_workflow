"""
Scanner model for CT scanner resource management
"""

from sqlalchemy import Column, String, Integer, DateTime, Boolean, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from src.database import Base


class ScannerStatus(str, enum.Enum):
    """CT Scanner status."""
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class ScannerType(str, enum.Enum):
    """CT Scanner type."""
    STANDARD = "standard"
    ADVANCED = "advanced"  # 128-slice or higher
    DUAL_SOURCE = "dual_source"


class Scanner(Base):
    """CT Scanner model for resource management."""

    __tablename__ = "scanners"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scanner_code = Column(String(50), unique=True, index=True, nullable=False)  # e.g., "CT-01"
    name = Column(String(255), nullable=False)
    location = Column(String(100))  # e.g., "Radiology Department, Room 205"

    # Scanner specifications
    scanner_type = Column(SQLEnum(ScannerType), default=ScannerType.STANDARD)
    slice_count = Column(Integer)  # e.g., 64, 128, 256
    manufacturer = Column(String(100))
    model = Column(String(100))
    serial_number = Column(String(100))

    # Status
    status = Column(SQLEnum(ScannerStatus), default=ScannerStatus.AVAILABLE)

    # Availability
    is_active = Column(Boolean, default=True)
    operational_hours_start = Column(String(10), default="08:00")  # e.g., "08:00"
    operational_hours_end = Column(String(10), default="22:00")    # e.g., "22:00"

    # Capacity planning
    avg_scan_duration_minutes = Column(Integer, default=30)  # Average scan duration
    daily_capacity = Column(Integer, default=40)  # Max scans per day

    # Current utilization
    today_scans_completed = Column(Integer, default=0)
    today_scans_scheduled = Column(Integer, default=0)
    current_utilization = Column(Float, default=0.0)  # Percentage

    # Maintenance
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    maintenance_notes = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    scans = relationship("CTScan", back_populates="scanner")

    def __repr__(self):
        return f"<Scanner {self.scanner_code} - {self.status.value}>"