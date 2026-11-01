from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database import Base


class MachineStateEvent(Base):
    __tablename__ = "machine_state_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(String(50), ForeignKey("machines.id"), nullable=False, index=True)
    plant_id = Column(String(50), ForeignKey("plants.id"), nullable=False, index=True)
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=False, index=True)  # RUNNING, IDLE, TRIPPED, EMERGENCY_STOP, MAINTENANCE, UNSAFE
    reason = Column(String(255), nullable=True)
    operator_shift_id = Column(String(50), ForeignKey("operator_shifts.id"), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    # Relationships
    machine = relationship("Machine", back_populates="state_events")
    operator_shift = relationship("OperatorShift", back_populates="state_events")

    __table_args__ = (
        Index("ix_state_events_machine_time", "machine_id", "timestamp"),
        Index("ix_state_events_plant_time", "plant_id", "timestamp"),
    )
