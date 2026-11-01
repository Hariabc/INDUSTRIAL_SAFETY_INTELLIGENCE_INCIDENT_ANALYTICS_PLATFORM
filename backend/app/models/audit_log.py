from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from backend.app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_name = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, VERIFY, EXECUTE
    actor = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)  # SLA, THRESHOLD, DETECTION, MAPPING
    description = Column(String(500), nullable=True)
    updated_by = Column(String(100), default="SYSTEM")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
