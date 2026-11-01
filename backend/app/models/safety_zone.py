from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class SafetyZone(Base):
    __tablename__ = "safety_zones"

    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    zone_type = Column(String(50), default="CONTROLLED")  # HAZARDOUS, EXCLUSION, CONTROLLED, GENERAL
    hazard_level = Column(String(50), default="MEDIUM")  # HIGH, MEDIUM, LOW
    max_occupancy = Column(Integer, default=5)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    plant = relationship("Plant", back_populates="safety_zones")
    machine_associations = relationship("MachineSafetyZone", back_populates="safety_zone", cascade="all, delete-orphan")
    incidents = relationship("Incident", back_populates="safety_zone")


class MachineSafetyZone(Base):
    __tablename__ = "machine_safety_zones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    safety_zone_id = Column(String(50), ForeignKey("safety_zones.id"), nullable=False, index=True)
    coverage_type = Column(String(50), default="PRIMARY")  # PRIMARY, SECONDARY
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    machine = relationship("Machine", back_populates="safety_zone_associations")
    safety_zone = relationship("SafetyZone", back_populates="machine_associations")
