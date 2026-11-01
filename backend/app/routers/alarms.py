from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
from backend.app.database import get_db
from backend.app.models import AlarmEvent, AlarmDefinition, Machine, Plant, Acknowledgement

router = APIRouter(prefix="/alarms", tags=["Alarms"])


@router.get("")
def list_alarms(
    plant_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    is_nuisance: Optional[bool] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "event_timestamp",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """Paginated list of alarms with filtering across plants, machines, and severities."""
    query = db.query(AlarmEvent)

    if plant_id:
        query = query.filter(AlarmEvent.plant_id == plant_id)
    if machine_id:
        query = query.filter(AlarmEvent.machine_id == machine_id)
    if severity:
        query = query.filter(AlarmEvent.severity == severity)
    if status:
        query = query.filter(AlarmEvent.status == status)
    if is_nuisance is not None:
        query = query.filter(AlarmEvent.is_nuisance == is_nuisance)

    if start_date:
        try:
            st = datetime.fromisoformat(start_date)
            query = query.filter(AlarmEvent.event_timestamp >= st)
        except Exception:
            pass

    if end_date:
        try:
            et = datetime.fromisoformat(end_date)
            query = query.filter(AlarmEvent.event_timestamp <= et)
        except Exception:
            pass

    if search:
        search_filter = or_(
            AlarmEvent.id.ilike(f"%{search}%"),
            AlarmEvent.machine_id.ilike(f"%{search}%"),
            AlarmEvent.source_event_id.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()

    sort_col = getattr(AlarmEvent, sort_by, AlarmEvent.event_timestamp)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    alarms = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in alarms:
        items.append({
            "id": a.id,
            "alarm_definition_id": a.alarm_definition_id,
            "machine_id": a.machine_id,
            "plant_id": a.plant_id,
            "severity": a.severity,
            "source_event_id": a.source_event_id,
            "value": a.value,
            "threshold": a.threshold,
            "unit": a.unit,
            "status": a.status,
            "event_timestamp": a.event_timestamp.isoformat(),
            "cleared_timestamp": a.cleared_timestamp.isoformat() if a.cleared_timestamp else None,
            "is_nuisance": a.is_nuisance,
        })

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{alarm_id}")
def get_alarm_detail(alarm_id: str, db: Session = Depends(get_db)):
    """Get full details for an alarm event, its definition, and acknowledgement."""
    alarm = db.query(AlarmEvent).filter(AlarmEvent.id == alarm_id).first()
    if not alarm:
        raise HTTPException(status_code=404, detail="Alarm event not found")

    definition = db.query(AlarmDefinition).filter(AlarmDefinition.id == alarm.alarm_definition_id).first()
    machine = db.query(Machine).filter(Machine.id == alarm.machine_id).first()
    plant = db.query(Plant).filter(Plant.id == alarm.plant_id).first()
    ack = db.query(Acknowledgement).filter(Acknowledgement.alarm_event_id == alarm.id).first()

    return {
        "alarm": {
            "id": alarm.id,
            "severity": alarm.severity,
            "status": alarm.status,
            "source_event_id": alarm.source_event_id,
            "value": alarm.value,
            "threshold": alarm.threshold,
            "unit": alarm.unit,
            "event_timestamp": alarm.event_timestamp.isoformat(),
            "cleared_timestamp": alarm.cleared_timestamp.isoformat() if alarm.cleared_timestamp else None,
            "is_nuisance": alarm.is_nuisance,
        },
        "definition": {
            "id": definition.id if definition else alarm.alarm_definition_id,
            "code": definition.code if definition else "N/A",
            "name": definition.name if definition else "N/A",
            "category": definition.category if definition else "N/A",
            "ack_sla_seconds": definition.ack_sla_seconds if definition else 1800,
        },
        "machine": {
            "id": machine.id if machine else alarm.machine_id,
            "name": machine.name if machine else alarm.machine_id,
            "current_state": machine.current_state if machine else "UNKNOWN",
        },
        "plant": {
            "id": plant.id if plant else alarm.plant_id,
            "name": plant.name if plant else alarm.plant_id,
        },
        "acknowledgement": {
            "id": ack.id,
            "operator_name": ack.operator_name,
            "ack_timestamp": ack.ack_timestamp.isoformat(),
            "ack_delay_seconds": ack.ack_delay_seconds,
            "sla_status": ack.sla_status,
            "notes": ack.notes,
        } if ack else None
    }
