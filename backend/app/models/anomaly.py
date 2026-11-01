from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Index, Text
from backend.app.database import Base


class SafetyAnomaly(Base):
    __tablename__ = "safety_anomalies"

    id = Column(String(50), primary_key=True, index=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=True, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=True, index=True)
    anomaly_type = Column(String(100), nullable=False, index=True)
    # Types: REPEATED_UNSAFE_CONDITION, DELAYED_ACKNOWLEDGEMENT, ALARM_FLOOD, NUISANCE_ALARM,
    #        INTERLOCK_VIOLATION, MISSING_INCIDENT_CONTEXT, DUPLICATE_ALARM_REPLAY, INCOMPLETE_CORRECTIVE_ACTION
    severity = Column(String(50), nullable=False, index=True)  # CRITICAL, HIGH, MEDIUM, LOW
    detection_timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    related_event_ids = Column(Text, nullable=True)  # Comma or JSON array of related IDs
    explanation = Column(Text, nullable=False)
    recommended_action = Column(Text, nullable=False)
    status = Column(String(50), default="DETECTED", index=True)  # DETECTED, INVESTIGATING, CONFIRMED, DISMISSED
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_anomalies_type_severity", "anomaly_type", "severity"),
        Index("ix_anomalies_plant_status", "plant_id", "status"),
    )
