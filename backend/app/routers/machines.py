from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from backend.app.database import get_db
from backend.app.models import (
    Machine, Plant, SafetyZone, MachineSafetyZone, Interlock,
    AlarmEvent, Incident, MachineStateEvent
)

router = APIRouter(prefix="/machines", tags=["Machines"])


@router.get("")
def list_machines(
    plant_id: Optional[str] = None,
    state: Optional[str] = None,
    criticality: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    sort_by: str = "id",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    """List machines with filtering, search, and pagination."""
    query = db.query(Machine)

    if plant_id:
        query = query.filter(Machine.plant_id == plant_id)
    if state:
        query = query.filter(Machine.current_state == state)
    if criticality:
        query = query.filter(Machine.criticality == criticality)
    if search:
        search_filter = or_(
            Machine.id.ilike(f"%{search}%"),
            Machine.name.ilike(f"%{search}%"),
            Machine.type.ilike(f"%{search}%"),
            Machine.model_number.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()

    # Sorting
    sort_col = getattr(Machine, sort_by, Machine.id)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    machines = query.offset((page - 1) * page_size).limit(page_size).all()

    # Augment with plant name and alarm counts
    items = []
    for m in machines:
        plant = db.query(Plant.name).filter(Plant.id == m.plant_id).first()
        alm_count = db.query(AlarmEvent).filter(AlarmEvent.machine_id == m.id).count()
        inc_count = db.query(Incident).filter(Incident.machine_id == m.id).count()
        last_evt = db.query(AlarmEvent.event_timestamp).filter(AlarmEvent.machine_id == m.id).order_by(AlarmEvent.event_timestamp.desc()).first()

        items.append({
            "id": m.id,
            "plant_id": m.plant_id,
            "plant_name": plant[0] if plant else m.plant_id,
            "name": m.name,
            "type": m.type,
            "model_number": m.model_number,
            "installation_date": m.installation_date.isoformat(),
            "current_state": m.current_state,
            "criticality": m.criticality,
            "is_isolated": m.is_isolated,
            "alarm_count": alm_count,
            "incident_count": inc_count,
            "last_event_timestamp": last_evt[0].isoformat() if last_evt else None,
        })

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{machine_id}")
def get_machine_detail(machine_id: str, db: Session = Depends(get_db)):
    """Get detailed machine configuration, interlocks, and safety zones."""
    m = db.query(Machine).filter(Machine.id == machine_id).first()
    if not m:
        raise HTTPException(status_code=404, detail="Machine not found")

    plant = db.query(Plant).filter(Plant.id == m.plant_id).first()
    itls = db.query(Interlock).filter(Interlock.machine_id == machine_id).all()

    # Zones via bridge
    zones = (
        db.query(SafetyZone, MachineSafetyZone.coverage_type)
        .join(MachineSafetyZone, SafetyZone.id == MachineSafetyZone.safety_zone_id)
        .filter(MachineSafetyZone.machine_id == machine_id)
        .all()
    )

    alm_count = db.query(AlarmEvent).filter(AlarmEvent.machine_id == machine_id).count()
    crit_alm_count = db.query(AlarmEvent).filter(
        AlarmEvent.machine_id == machine_id,
        AlarmEvent.severity == "CRITICAL"
    ).count()
    inc_count = db.query(Incident).filter(Incident.machine_id == machine_id).count()

    return {
        "machine": {
            "id": m.id,
            "plant_id": m.plant_id,
            "plant_name": plant.name if plant else m.plant_id,
            "name": m.name,
            "type": m.type,
            "model_number": m.model_number,
            "installation_date": m.installation_date.isoformat(),
            "current_state": m.current_state,
            "criticality": m.criticality,
            "is_isolated": m.is_isolated,
        },
        "stats": {
            "total_alarms": alm_count,
            "critical_alarms": crit_alm_count,
            "incidents": inc_count,
        },
        "interlocks": [
            {
                "id": itl.id,
                "name": itl.name,
                "interlock_type": itl.interlock_type,
                "target_state": itl.target_state,
                "current_state": itl.current_state,
                "is_safety_critical": itl.is_safety_critical,
                "bypass_allowed": itl.bypass_allowed,
                "last_tested_at": itl.last_tested_at.isoformat() if itl.last_tested_at else None,
            }
            for itl in itls
        ],
        "safety_zones": [
            {
                "id": z.id,
                "name": z.name,
                "zone_type": z.zone_type,
                "hazard_level": z.hazard_level,
                "coverage_type": cov_type,
            }
            for z, cov_type in zones
        ]
    }


@router.get("/{machine_id}/history")
def get_machine_history(machine_id: str, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve immutable machine state transitions and recent alarm timeline."""
    states = (
        db.query(MachineStateEvent)
        .filter(MachineStateEvent.machine_id == machine_id)
        .order_by(MachineStateEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    recent_alarms = (
        db.query(AlarmEvent)
        .filter(AlarmEvent.machine_id == machine_id)
        .order_by(AlarmEvent.event_timestamp.desc())
        .limit(limit)
        .all()
    )

    return {
        "machine_id": machine_id,
        "state_transitions": [
            {
                "id": s.id,
                "previous_state": s.previous_state,
                "new_state": s.new_state,
                "reason": s.reason,
                "timestamp": s.timestamp.isoformat(),
            }
            for s in states
        ],
        "recent_alarms": [
            {
                "id": a.id,
                "severity": a.severity,
                "value": a.value,
                "unit": a.unit,
                "status": a.status,
                "timestamp": a.event_timestamp.isoformat(),
            }
            for a in recent_alarms
        ]
    }
