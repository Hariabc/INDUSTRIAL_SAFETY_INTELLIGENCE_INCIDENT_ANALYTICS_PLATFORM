from sqlalchemy import Column, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base, utcnow


class OperatorShift(Base):
    __tablename__ = "operator_shifts"

    id = Column(String(50), primary_key=True, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    shift_name = Column(String(50), nullable=False)  # MORNING, AFTERNOON, NIGHT
    lead_operator_name = Column(String(100), nullable=False)
    shift_start = Column(DateTime, nullable=False, index=True)
    shift_end = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, default=utcnow)

    # Relationships
    plant = relationship("Plant", back_populates="shifts")
    state_events = relationship("MachineStateEvent", back_populates="operator_shift")
    acknowledgements = relationship("Acknowledgement", back_populates="operator_shift")
    incidents = relationship("Incident", back_populates="operator_shift")

    __table_args__ = (
        Index("ix_operator_shifts_plant_time", "plant_id", "shift_start", "shift_end"),
    )
