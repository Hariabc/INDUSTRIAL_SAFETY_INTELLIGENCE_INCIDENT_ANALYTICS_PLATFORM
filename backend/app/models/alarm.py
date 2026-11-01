from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class AlarmDefinition(Base):
    __tablename__ = "alarm_definitions"

    id = Column(String(50), primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    severity = Column(String(50), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    category = Column(String(100), nullable=False, index=True)  # SAFETY_INTERLOCK, OVERHEATING, PRESSURE_ANOMALY, VIBRATION, EMERGENCY_SHUTDOWN, TOXIC_GAS, ELECTRICAL_FAULT
    ack_sla_seconds = Column(Integer, nullable=False, default=1800)
    requires_clearance = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    events = relationship("AlarmEvent", back_populates="definition")


class AlarmEvent(Base):
    __tablename__ = "alarm_events"

    id = Column(String(50), primary_key=True, index=True)
    alarm_definition_id = Column(String(50), ForeignKey("alarm_definitions.id"), nullable=False, index=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    source_event_id = Column(String(100), nullable=False, index=True)  # Traceable raw identifier
    value = Column(Float, nullable=True)
    threshold = Column(Float, nullable=True)
    unit = Column(String(20), nullable=True)
    status = Column(String(50), default="ACTIVE", index=True)  # ACTIVE, ACKNOWLEDGED, CLEARED, SUPPRESSED
    event_timestamp = Column(DateTime, nullable=False, index=True)
    cleared_timestamp = Column(DateTime, nullable=True)
    is_nuisance = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    definition = relationship("AlarmDefinition", back_populates="events")
    machine = relationship("Machine", back_populates="alarm_events")
    plant = relationship("Plant", back_populates="alarm_events")
    acknowledgements = relationship("Acknowledgement", back_populates="alarm_event", cascade="all, delete-orphan")
    incident_associations = relationship("IncidentAlarmEvent", back_populates="alarm_event")

    __table_args__ = (
        Index("ix_alarm_events_machine_time", "machine_id", "event_timestamp"),
        Index("ix_alarm_events_plant_time", "plant_id", "event_timestamp"),
        Index("ix_alarm_events_source_event", "source_event_id"),
        Index("ix_alarm_events_severity_time", "severity", "event_timestamp"),
    )


class Acknowledgement(Base):
    __tablename__ = "acknowledgements"

    id = Column(String(50), primary_key=True, index=True)
    alarm_event_id = Column(String(50), ForeignKey("alarm_events.id"), nullable=False, index=True)
    operator_name = Column(String(100), nullable=False)
    operator_shift_id = Column(String(50), ForeignKey("operator_shifts.id"), nullable=True)
    ack_timestamp = Column(DateTime, nullable=False, index=True)
    ack_delay_seconds = Column(Float, nullable=False)
    sla_status = Column(String(50), nullable=False, index=True)  # WITHIN_SLA, DELAYED, ANOMALOUS_PRE_ALARM
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    alarm_event = relationship("AlarmEvent", back_populates="acknowledgements")
    operator_shift = relationship("OperatorShift", back_populates="acknowledgements")

    __table_args__ = (
        Index("ix_acknowledgements_alarm_time", "alarm_event_id", "ack_timestamp"),
        Index("ix_acknowledgements_sla_status", "sla_status"),
    )
