from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel
from typing import Dict, Any, List
from backend.app.database import get_db
from backend.app.models import SystemConfig, AuditLog
from backend.app.config import settings

router = APIRouter(prefix="/settings", tags=["System Settings"])


class SettingsUpdateRequest(BaseModel):
    ack_sla_critical_seconds: int = 300
    ack_sla_high_seconds: int = 900
    ack_sla_medium_seconds: int = 1800
    ack_sla_low_seconds: int = 3600
    alarm_flood_threshold: int = 10
    alarm_flood_window_minutes: int = 10
    repeated_unsafe_window_hours: int = 24
    repeated_unsafe_min_events: int = 3
    nuisance_alarm_min_count: int = 15
    nuisance_max_incident_rate: float = 0.05
    actor: str = "Administrator"


@router.get("")
def get_system_settings(db: Session = Depends(get_db)):
    """Retrieve active SLA, detection threshold parameters, and audit history."""
    # Read any custom database overrides
    configs = db.query(SystemConfig).all()
    override_dict = {c.key: c.value for c in configs}

    current_settings = {
        "ack_sla_critical_seconds": int(override_dict.get("ACK_SLA_CRITICAL_SECONDS", settings.ACK_SLA_CRITICAL_SECONDS)),
        "ack_sla_high_seconds": int(override_dict.get("ACK_SLA_HIGH_SECONDS", settings.ACK_SLA_HIGH_SECONDS)),
        "ack_sla_medium_seconds": int(override_dict.get("ACK_SLA_MEDIUM_SECONDS", settings.ACK_SLA_MEDIUM_SECONDS)),
        "ack_sla_low_seconds": int(override_dict.get("ACK_SLA_LOW_SECONDS", settings.ACK_SLA_LOW_SECONDS)),
        "alarm_flood_threshold": int(override_dict.get("ALARM_FLOOD_THRESHOLD", settings.ALARM_FLOOD_THRESHOLD)),
        "alarm_flood_window_minutes": int(override_dict.get("ALARM_FLOOD_WINDOW_MINUTES", settings.ALARM_FLOOD_WINDOW_MINUTES)),
        "repeated_unsafe_window_hours": int(override_dict.get("REPEATED_UNSAFE_WINDOW_HOURS", settings.REPEATED_UNSAFE_WINDOW_HOURS)),
        "repeated_unsafe_min_events": int(override_dict.get("REPEATED_UNSAFE_MIN_EVENTS", settings.REPEATED_UNSAFE_MIN_EVENTS)),
        "nuisance_alarm_min_count": int(override_dict.get("NUISANCE_ALARM_MIN_COUNT", settings.NUISANCE_ALARM_MIN_COUNT)),
        "nuisance_max_incident_rate": float(override_dict.get("NUISANCE_MAX_INCIDENT_RATE", settings.NUISANCE_MAX_INCIDENT_RATE)),
    }

    # Fetch recent audit logs
    recent_audits = (
        db.query(AuditLog)
        .order_by(AuditLog.timestamp.desc())
        .limit(20)
        .all()
    )

    return {
        "settings": current_settings,
        "audit_logs": [
            {
                "id": a.id,
                "entity_name": a.entity_name,
                "entity_id": a.entity_id,
                "action": a.action,
                "actor": a.actor,
                "details": a.details,
                "timestamp": a.timestamp.isoformat(),
            }
            for a in recent_audits
        ]
    }


@router.post("")
def update_system_settings(payload: SettingsUpdateRequest, db: Session = Depends(get_db)):
    """Update SLA and detection thresholds with validation and audit trail."""
    # Validation
    if payload.ack_sla_critical_seconds <= 0 or payload.alarm_flood_threshold <= 0:
        raise HTTPException(status_code=400, detail="Thresholds must be strictly positive integers.")

    param_map = {
        "ACK_SLA_CRITICAL_SECONDS": (str(payload.ack_sla_critical_seconds), "SLA", "Critical Alarm Ack SLA (seconds)"),
        "ACK_SLA_HIGH_SECONDS": (str(payload.ack_sla_high_seconds), "SLA", "High Alarm Ack SLA (seconds)"),
        "ACK_SLA_MEDIUM_SECONDS": (str(payload.ack_sla_medium_seconds), "SLA", "Medium Alarm Ack SLA (seconds)"),
        "ACK_SLA_LOW_SECONDS": (str(payload.ack_sla_low_seconds), "SLA", "Low Alarm Ack SLA (seconds)"),
        "ALARM_FLOOD_THRESHOLD": (str(payload.alarm_flood_threshold), "DETECTION", "Alarm Flood Count Threshold"),
        "ALARM_FLOOD_WINDOW_MINUTES": (str(payload.alarm_flood_window_minutes), "DETECTION", "Alarm Flood Window (minutes)"),
        "REPEATED_UNSAFE_WINDOW_HOURS": (str(payload.repeated_unsafe_window_hours), "DETECTION", "Repeated Unsafe Condition Window (hours)"),
        "REPEATED_UNSAFE_MIN_EVENTS": (str(payload.repeated_unsafe_min_events), "DETECTION", "Min Events for Repeated Unsafe Alert"),
        "NUISANCE_ALARM_MIN_COUNT": (str(payload.nuisance_alarm_min_count), "DETECTION", "Nuisance Alarm Trigger Count"),
        "NUISANCE_MAX_INCIDENT_RATE": (str(payload.nuisance_max_incident_rate), "DETECTION", "Nuisance Alarm Max Incident Conversion"),
    }

    for key, (val, cat, desc) in param_map.items():
        existing = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if existing:
            existing.value = val
            existing.updated_by = payload.actor
            existing.updated_at = datetime.utcnow()
        else:
            db.add(SystemConfig(
                key=key,
                value=val,
                category=cat,
                description=desc,
                updated_by=payload.actor,
                updated_at=datetime.utcnow()
            ))

    audit = AuditLog(
        entity_name="SystemConfig",
        entity_id="GLOBAL",
        action="UPDATE_CONFIG",
        actor=payload.actor,
        details=f"Updated SLA and detection parameters: critical_sla={payload.ack_sla_critical_seconds}s, flood_thresh={payload.alarm_flood_threshold}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {"message": "Configuration parameters successfully updated and audited.", "updated_by": payload.actor}
