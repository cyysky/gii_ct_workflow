"""
FAQ model for patient education and chatbot
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean
from datetime import datetime
import uuid

from src.database import Base


class FAQ(Base):
    """FAQ model for patient questions about CT Brain procedure."""

    __tablename__ = "faqs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Category for organization
    category = Column(String(100), index=True)  # e.g., "procedure", "preparation", "risks", "results"

    # Keywords for semantic search
    keywords = Column(Text)  # Comma-separated keywords

    # Language support
    language = Column(String(10), default="en")

    # Embedding vector (stored as text for simplicity, could be vector in production)
    embedding = Column(Text)

    # Usage tracking
    view_count = Column(Integer, default=0)
    helpful_count = Column(Integer, default=0)
    not_helpful_count = Column(Integer, default=0)

    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<FAQ {self.category}: {self.question[:50]}...>"