from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    safety_zone_id = Column(String(50), ForeignKey("safety_zones.id"), nullable=True, index=True)
    triggering_alarm_id = Column(String(50), ForeignKey("alarm_events.id"), nullable=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=True)
    incident_type = Column(String(50), nullable=False, index=True)  # NEAR_MISS, EQUIPMENT_DAMAGE, SAFETY_BREACH, HAZARDOUS_RELEASE, INTERLOCK_FAILURE
    severity = Column(String(50), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    status = Column(String(50), default="OPEN", index=True)  # OPEN, INVESTIGATING, CONTAINED, RESOLVED, CLOSED
    assigned_investigator = Column(String(100), nullable=True)
    operator_shift_id = Column(String(50), ForeignKey("operator_shifts.id"), nullable=True)
    created_timestamp = Column(DateTime, nullable=False, index=True)
    contained_timestamp = Column(DateTime, nullable=True)
    resolved_timestamp = Column(DateTime, nullable=True)
    closed_timestamp = Column(DateTime, nullable=True)

    # Relationships
    plant = relationship("Plant", back_populates="incidents")
    machine = relationship("Machine", back_populates="incidents")
    safety_zone = relationship("SafetyZone", back_populates="incidents")
    triggering_alarm = relationship("AlarmEvent", foreign_keys=[triggering_alarm_id])
    operator_shift = relationship("OperatorShift", back_populates="incidents")
    corrective_actions = relationship("CorrectiveAction", back_populates="incident", cascade="all, delete-orphan")
    alarm_associations = relationship("IncidentAlarmEvent", back_populates="incident", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_incidents_plant_status", "plant_id", "status"),
        Index("ix_incidents_machine_severity", "machine_id", "severity"),
        Index("ix_incidents_created_time", "created_timestamp"),
    )


class IncidentAlarmEvent(Base):
    __tablename__ = "incident_alarm_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    incident_id = Column(String(50), ForeignKey("incidents.id"), nullable=False, index=True)
    alarm_event_id = Column(String(50), ForeignKey("alarm_events.id"), nullable=False, index=True)
    relationship_type = Column(String(50), default="TRIGGER")  # TRIGGER, CONSEQUENTIAL, CORRELATED
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    incident = relationship("Incident", back_populates="alarm_associations")
    alarm_event = relationship("AlarmEvent", back_populates="incident_associations")
