from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Interlock(Base):
    __tablename__ = "interlocks"

    id = Column(String(50), primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    interlock_type = Column(String(50), nullable=False)  # HARDWARE_GUARD, PRESSURE_RELIEF, E_STOP_CIRCUIT, THERMAL_CUTOFF, LIGHT_CURTAIN
    target_state = Column(String(50), default="ENGAGED")  # ENGAGED, DISENGAGED, BYPASSED, FAULT
    current_state = Column(String(50), default="ENGAGED")  # ENGAGED, DISENGAGED, BYPASSED, FAULT
    is_safety_critical = Column(Boolean, default=True)
    bypass_allowed = Column(Boolean, default=False)
    last_tested_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    machine = relationship("Machine", back_populates="interlocks")

    __table_args__ = (
        Index("ix_interlocks_machine_state", "machine_id", "current_state"),
    )
