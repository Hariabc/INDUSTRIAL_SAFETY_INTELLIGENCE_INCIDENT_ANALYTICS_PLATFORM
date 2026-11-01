from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Plant(Base):
    __tablename__ = "plants"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    location = Column(String(200), nullable=False)
    operational_status = Column(String(50), default="ACTIVE")
    total_lines = Column(Integer, default=4)
    safety_score = Column(Float, default=95.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    machines = relationship("Machine", back_populates="plant", cascade="all, delete-orphan")
    safety_zones = relationship("SafetyZone", back_populates="plant", cascade="all, delete-orphan")
    shifts = relationship("OperatorShift", back_populates="plant")
    alarm_events = relationship("AlarmEvent", back_populates="plant")
    incidents = relationship("Incident", back_populates="plant")
