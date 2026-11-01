from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class Machine(Base):
    __tablename__ = "machines"

    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    type = Column(String(50), nullable=False)  # TURBINE, ROBOTIC_ARM, HYDRAULIC_PRESS, CONVEYOR, COMPRESSOR, REACTOR, CNC_MILL
    model_number = Column(String(100))
    installation_date = Column(DateTime, default=utcnow)
    current_state = Column(String(50), default="RUNNING", index=True)  # RUNNING, IDLE, TRIPPED, EMERGENCY_STOP, MAINTENANCE, UNSAFE
    criticality = Column(String(50), default="MEDIUM", index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    is_isolated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    # Relationships
    plant = relationship("Plant", back_populates="machines")
    safety_zone_associations = relationship("MachineSafetyZone", back_populates="machine", cascade="all, delete-orphan")
    interlocks = relationship("Interlock", back_populates="machine", cascade="all, delete-orphan")
    state_events = relationship("MachineStateEvent", back_populates="machine", cascade="all, delete-orphan")
    alarm_events = relationship("AlarmEvent", back_populates="machine", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="machine")

    __table_args__ = (
        Index("ix_machines_plant_state", "plant_id", "current_state"),
        Index("ix_machines_criticality", "criticality"),
    )
