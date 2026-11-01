from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"

    id = Column(String(50), primary_key=True, index=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    assigned_to = Column(String(100), nullable=False)
    priority = Column(String(50), default="HIGH", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDING", index=True)  # PENDING, IN_PROGRESS, COMPLETED, CLOSED, CANCELLED
    verification_required = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False, index=True)
    verified_by = Column(String(100), nullable=True)
    verified_at = Column(DateTime, nullable=True)
    verification_notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="corrective_actions")

    __table_args__ = (
        Index("ix_corrective_actions_incident_status", "incident_id", "status"),
        Index("ix_corrective_actions_priority_due", "priority", "due_date"),
    )
