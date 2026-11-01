from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from backend.app.database import get_db
from backend.app.models import (
    AlarmEvent, Machine, Plant, Incident, Acknowledgement
)
from backend.app.services.evaluation_service import ModelEvaluationService

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/alarm-trends")
def get_alarm_trends(
    plant_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    days: int = Query(30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Aggregate alarm counts over daily time intervals broken down by severity."""
    query = db.query(
        func.date(AlarmEvent.event_timestamp).label("day"),
        AlarmEvent.severity,
        func.count(AlarmEvent.id).label("cnt")
    )

    if plant_id:
        query = query.filter(AlarmEvent.plant_id == plant_id)
    if machine_id:
        query = query.filter(AlarmEvent.machine_id == machine_id)

    records = query.group_by("day", AlarmEvent.severity).order_by("day").all()

    # Aggregate into daily structures
    trend_map = {}
    for day_val, sev, count in records:
        day_str = str(day_val)
        if day_str not in trend_map:
            trend_map[day_str] = {
                "date": day_str,
                "CRITICAL": 0,
                "HIGH": 0,
                "MEDIUM": 0,
                "LOW": 0,
                "INFO": 0,
                "total": 0,
            }
        trend_map[day_str][sev] = count
        trend_map[day_str]["total"] += count

    points = list(trend_map.values())
    points.sort(key=lambda x: x["date"])
    return points


@router.get("/severity-distribution")
def get_severity_distribution(
    plant_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Calculate alarm count distribution across severity tiers."""
    query = db.query(AlarmEvent.severity, func.count(AlarmEvent.id).label("cnt"))

    if plant_id:
        query = query.filter(AlarmEvent.plant_id == plant_id)
    if machine_id:
        query = query.filter(AlarmEvent.machine_id == machine_id)

    records = query.group_by(AlarmEvent.severity).all()
    total = sum(r[1] for r in records) or 1

    colors = {
        "CRITICAL": "#ef4444",
        "HIGH": "#f97316",
        "MEDIUM": "#eab308",
        "LOW": "#3b82f6",
        "INFO": "#06b6d4",
    }

    results = []
    for sev, count in records:
        results.append({
            "severity": sev,
            "count": count,
            "percentage": round((count / total) * 100.0, 2),
            "color": colors.get(sev, "#94a3b8"),
        })

    # Ensure consistent order
    sev_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    results.sort(key=lambda x: sev_order.index(x["severity"]) if x["severity"] in sev_order else 99)
    return results


@router.get("/unsafe-machines")
def get_unsafe_machines(limit: int = 10, db: Session = Depends(get_db)):
    """Top machinery exhibiting repeated unsafe conditions, critical alarms, and trips."""
    top_records = (
        db.query(
            Machine.id,
            Machine.name,
            Machine.plant_id,
            Machine.current_state,
            Machine.criticality,
            func.count(AlarmEvent.id).label("total_alarms"),
        )
        .join(AlarmEvent, Machine.id == AlarmEvent.machine_id)
        .group_by(Machine.id, Machine.name, Machine.plant_id, Machine.current_state, Machine.criticality)
        .order_by(func.count(AlarmEvent.id).desc())
        .limit(limit)
        .all()
    )

    results = []
    for m_id, m_name, p_id, state, crit, total_alms in top_records:
        plant = db.query(Plant.name).filter(Plant.id == p_id).first()
        crit_alms = db.query(AlarmEvent).filter(
            AlarmEvent.machine_id == m_id,
            AlarmEvent.severity == "CRITICAL"
        ).count()
        inc_count = db.query(Incident).filter(Incident.machine_id == m_id).count()

        results.append({
            "machine_id": m_id,
            "machine_name": m_name,
            "plant_id": p_id,
            "plant_name": plant[0] if plant else p_id,
            "current_state": state,
            "criticality": crit,
            "total_alarms": total_alms,
            "critical_alarms": crit_alms,
            "incident_count": inc_count,
        })

    return results


@router.get("/acknowledgement-performance")
def get_acknowledgement_performance(plant_id: Optional[str] = None, db: Session = Depends(get_db)):
    """Acknowledgement latency distribution and SLA adherence performance."""
    total_acks = db.query(Acknowledgement).count()
    within_sla = db.query(Acknowledgement).filter(Acknowledgement.sla_status == "WITHIN_SLA").count()
    delayed = db.query(Acknowledgement).filter(Acknowledgement.sla_status == "DELAYED").count()
    anomalous_pre = db.query(Acknowledgement).filter(Acknowledgement.sla_status == "ANOMALOUS_PRE_ALARM").count()

    avg_delay = db.query(func.avg(Acknowledgement.ack_delay_seconds)).filter(Acknowledgement.ack_delay_seconds >= 0).scalar() or 0.0

    return {
        "total_acknowledgements": total_acks,
        "within_sla": within_sla,
        "delayed": delayed,
        "anomalous_pre_alarm": anomalous_pre,
        "sla_adherence_rate": round((within_sla / total_acks * 100.0), 2) if total_acks > 0 else 0.0,
        "delayed_rate": round((delayed / total_acks * 100.0), 2) if total_acks > 0 else 0.0,
        "average_ack_time_seconds": round(float(avg_delay), 2),
    }


@router.get("/model-evaluation")
def get_model_evaluation(db: Session = Depends(get_db)):
    """Evaluate detection engine against ground truth and return metrics and KPIs."""
    eval_svc = ModelEvaluationService(db)
    return eval_svc.evaluate()
