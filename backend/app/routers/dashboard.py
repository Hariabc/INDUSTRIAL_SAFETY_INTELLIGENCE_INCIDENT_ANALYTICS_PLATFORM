from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models import (
    Plant, Machine, AlarmEvent, Incident, CorrectiveAction, SafetyAnomaly
)
from backend.app.schemas.analytics import OverviewStatsSchema
from backend.app.services.evaluation_service import ModelEvaluationService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    """Executive summary metrics and recent high-priority activity."""
    total_plants = db.query(Plant).count()
    total_machines = db.query(Machine).count()
    total_alarms = db.query(AlarmEvent).count()
    critical_alarms = db.query(AlarmEvent).filter(AlarmEvent.severity == "CRITICAL").count()
    active_incidents = db.query(Incident).filter(Incident.status.in_(["OPEN", "INVESTIGATING", "CONTAINED"])).count()
    unresolved_actions = db.query(CorrectiveAction).filter(CorrectiveAction.status.in_(["PENDING", "IN_PROGRESS"])).count()

    # Calculate average safety score
    avg_score = db.query(func.avg(Plant.safety_score)).scalar() or 92.5

    # Get data integrity score from evaluation service
    eval_svc = ModelEvaluationService(db)
    eval_data = eval_svc.evaluate()
    data_integrity_score = eval_data["operational_kpis"]["data_integrity_score"]

    # Recent critical alarms
    recent_alarms = (
        db.query(AlarmEvent)
        .filter(AlarmEvent.severity == "CRITICAL")
        .order_by(AlarmEvent.event_timestamp.desc())
        .limit(6)
        .all()
    )

    # Recent high priority incidents
    recent_incidents = (
        db.query(Incident)
        .order_by(Incident.created_timestamp.desc())
        .limit(6)
        .all()
    )

    return {
        "stats": {
            "total_plants": total_plants,
            "total_machines": total_machines,
            "total_alarms": total_alarms,
            "critical_alarms": critical_alarms,
            "active_incidents": active_incidents,
            "unresolved_corrective_actions": unresolved_actions,
            "plant_safety_score": round(float(avg_score), 1),
            "data_integrity_score": data_integrity_score,
        },
        "recent_critical_alarms": [
            {
                "id": a.id,
                "machine_id": a.machine_id,
                "plant_id": a.plant_id,
                "severity": a.severity,
                "status": a.status,
                "timestamp": a.event_timestamp.isoformat(),
            }
            for a in recent_alarms
        ],
        "recent_incidents": [
            {
                "id": inc.id,
                "title": inc.title,
                "machine_id": inc.machine_id,
                "plant_id": inc.plant_id,
                "severity": inc.severity,
                "status": inc.status,
                "incident_type": inc.incident_type,
                "timestamp": inc.created_timestamp.isoformat(),
            }
            for inc in recent_incidents
        ]
    }
