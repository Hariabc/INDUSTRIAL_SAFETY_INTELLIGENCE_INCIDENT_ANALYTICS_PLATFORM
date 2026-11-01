import json
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.app.database import get_db
from backend.app.models import SafetyAnomaly, Plant, Machine
from backend.app.services.detection_engine import SafetyDetectionEngine
from backend.app.services.evaluation_service import ModelEvaluationService

router = APIRouter(prefix="", tags=["Safety Intelligence"])


@router.get("/anomalies")
def list_anomalies(
    anomaly_type: Optional[str] = None,
    severity: Optional[str] = None,
    plant_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    sort_by: str = "detection_timestamp",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """List detected safety anomalies and explainable intelligence findings."""
    query = db.query(SafetyAnomaly)

    if anomaly_type:
        query = query.filter(SafetyAnomaly.anomaly_type == anomaly_type)
    if severity:
        query = query.filter(SafetyAnomaly.severity == severity)
    if plant_id:
        query = query.filter(SafetyAnomaly.plant_id == plant_id)
    if machine_id:
        query = query.filter(SafetyAnomaly.machine_id == machine_id)
    if status:
        query = query.filter(SafetyAnomaly.status == status)

    if search:
        search_filter = or_(
            SafetyAnomaly.id.ilike(f"%{search}%"),
            SafetyAnomaly.explanation.ilike(f"%{search}%"),
            SafetyAnomaly.recommended_action.ilike(f"%{search}%"),
            SafetyAnomaly.machine_id.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()

    sort_col = getattr(SafetyAnomaly, sort_by, SafetyAnomaly.detection_timestamp)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    anomalies = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in anomalies:
        plant_name = None
        machine_name = None
        if a.plant_id:
            p = db.query(Plant.name).filter(Plant.id == a.plant_id).first()
            plant_name = p[0] if p else a.plant_id
        if a.machine_id:
            m = db.query(Machine.name).filter(Machine.id == a.machine_id).first()
            machine_name = m[0] if m else a.machine_id

        # Parse related events
        rel_events = []
        if a.related_event_ids:
            try:
                rel_events = json.loads(a.related_event_ids)
                if not isinstance(rel_events, list):
                    rel_events = [str(rel_events)]
            except Exception:
                rel_events = [x.strip() for x in a.related_event_ids.split(",")]

        items.append({
            "id": a.id,
            "machine_id": a.machine_id,
            "machine_name": machine_name,
            "plant_id": a.plant_id,
            "plant_name": plant_name,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "detection_timestamp": a.detection_timestamp.isoformat(),
            "related_event_ids": rel_events,
            "explanation": a.explanation,
            "recommended_action": a.recommended_action,
            "status": a.status,
            "created_at": a.created_at.isoformat(),
        })

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/anomalies/{anomaly_id}")
def get_anomaly_detail(anomaly_id: str, db: Session = Depends(get_db)):
    """Retrieve individual safety anomaly finding with full explanation and supporting events."""
    anomaly = db.query(SafetyAnomaly).filter(SafetyAnomaly.id == anomaly_id).first()
    if not anomaly:
        raise HTTPException(status_code=404, detail="Safety anomaly not found")

    rel_events = []
    if anomaly.related_event_ids:
        try:
            rel_events = json.loads(anomaly.related_event_ids)
            if not isinstance(rel_events, list):
                rel_events = [str(rel_events)]
        except Exception:
            rel_events = [x.strip() for x in anomaly.related_event_ids.split(",")]

    return {
        "id": anomaly.id,
        "machine_id": anomaly.machine_id,
        "plant_id": anomaly.plant_id,
        "anomaly_type": anomaly.anomaly_type,
        "severity": anomaly.severity,
        "detection_timestamp": anomaly.detection_timestamp.isoformat(),
        "related_event_ids": rel_events,
        "explanation": anomaly.explanation,
        "recommended_action": anomaly.recommended_action,
        "status": anomaly.status,
        "created_at": anomaly.created_at.isoformat(),
    }


@router.post("/detection/run")
def trigger_detection_run(db: Session = Depends(get_db)):
    """Execute all 8 safety detection rules on-demand and update intelligence anomalies."""
    engine = SafetyDetectionEngine(db)
    detections = engine.run_all_rules(persist_to_db=True)

    eval_svc = ModelEvaluationService(db)
    evaluation = eval_svc.evaluate()

    return {
        "message": "Safety anomaly detection pipeline executed successfully.",
        "detections_count": len(detections),
        "evaluation": evaluation,
    }
