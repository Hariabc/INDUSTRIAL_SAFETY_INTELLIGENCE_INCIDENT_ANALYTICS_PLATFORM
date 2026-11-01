from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional, List
from datetime import datetime
from backend.app.database import get_db
from backend.app.models import (
    Incident, Plant, Machine, SafetyZone, AlarmEvent, Acknowledgement,
    MachineStateEvent, CorrectiveAction, IncidentAlarmEvent, AuditLog
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])


@router.get("")
def list_incidents(
    plant_id: Optional[str] = None,
    machine_id: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    incident_type: Optional[str] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    sort_by: str = "created_timestamp",
    sort_order: str = "desc",
    db: Session = Depends(get_db)
):
    """List incidents with multi-parameter filtering, search, and pagination."""
    query = db.query(Incident)

    if plant_id:
        query = query.filter(Incident.plant_id == plant_id)
    if machine_id:
        query = query.filter(Incident.machine_id == machine_id)
    if severity:
        query = query.filter(Incident.severity == severity)
    if status:
        query = query.filter(Incident.status == status)
    if incident_type:
        query = query.filter(Incident.incident_type == incident_type)

    if search:
        search_filter = or_(
            Incident.id.ilike(f"%{search}%"),
            Incident.title.ilike(f"%{search}%"),
            Incident.description.ilike(f"%{search}%"),
            Incident.assigned_investigator.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()

    sort_col = getattr(Incident, sort_by, Incident.created_timestamp)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    incidents = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for inc in incidents:
        plant = db.query(Plant.name).filter(Plant.id == inc.plant_id).first()
        machine = db.query(Machine.name).filter(Machine.id == inc.machine_id).first()

        items.append({
            "id": inc.id,
            "plant_id": inc.plant_id,
            "plant_name": plant[0] if plant else inc.plant_id,
            "machine_id": inc.machine_id,
            "machine_name": machine[0] if machine else inc.machine_id,
            "safety_zone_id": inc.safety_zone_id,
            "triggering_alarm_id": inc.triggering_alarm_id,
            "title": inc.title,
            "incident_type": inc.incident_type,
            "severity": inc.severity,
            "status": inc.status,
            "assigned_investigator": inc.assigned_investigator,
            "created_timestamp": inc.created_timestamp.isoformat(),
            "resolved_timestamp": inc.resolved_timestamp.isoformat() if inc.resolved_timestamp else None,
            "closed_timestamp": inc.closed_timestamp.isoformat() if inc.closed_timestamp else None,
        })

    total_pages = (total + page_size - 1) // page_size

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }


@router.get("/{incident_id}")
def get_incident_detail(incident_id: str, db: Session = Depends(get_db)):
    """
    Get comprehensive incident detail with true, non-fabricated chronological timeline:
    1. Machine-state transitions
    2. Alarm generation
    3. Acknowledgement
    4. Incident creation
    5. Corrective action assignment
    6. Action completion
    7. Verification
    8. Incident closure
    """
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    plant = db.query(Plant).filter(Plant.id == inc.plant_id).first()
    machine = db.query(Machine).filter(Machine.id == inc.machine_id).first()
    zone = db.query(SafetyZone).filter(SafetyZone.id == inc.safety_zone_id).first() if inc.safety_zone_id else None
    actions = db.query(CorrectiveAction).filter(CorrectiveAction.incident_id == incident_id).all()

    # Timeline construction from authentic database records
    timeline = []

    # 1. Triggering alarm and its acknowledgement
    triggering_alarm = None
    if inc.triggering_alarm_id:
        triggering_alarm = db.query(AlarmEvent).filter(AlarmEvent.id == inc.triggering_alarm_id).first()

    if triggering_alarm:
        # Machine state transitions prior to or around triggering alarm
        prior_state = (
            db.query(MachineStateEvent)
            .filter(
                MachineStateEvent.machine_id == inc.machine_id,
                MachineStateEvent.timestamp <= triggering_alarm.event_timestamp
            )
            .order_by(MachineStateEvent.timestamp.desc())
            .first()
        )
        if prior_state:
            timeline.append({
                "stage": "Machine State Transition",
                "timestamp": prior_state.timestamp.isoformat(),
                "actor": f"Machine {inc.machine_id}",
                "event_id": f"MSE-{prior_state.id}",
                "details": f"Transitioned to state '{prior_state.new_state}': {prior_state.reason or 'Normal operation'}",
                "badge_color": "cyan"
            })

        # 2. Alarm generation
        timeline.append({
            "stage": "Alarm Raised",
            "timestamp": triggering_alarm.event_timestamp.isoformat(),
            "actor": f"Machine {inc.machine_id}",
            "event_id": triggering_alarm.id,
            "details": f"Triggering alarm {triggering_alarm.id} ({triggering_alarm.severity}) raised: telemetry value {triggering_alarm.value or ''} {triggering_alarm.unit or ''}",
            "badge_color": "red"
        })

        # 3. Acknowledgement
        ack = db.query(Acknowledgement).filter(Acknowledgement.alarm_event_id == triggering_alarm.id).first()
        if ack:
            timeline.append({
                "stage": "Alarm Acknowledged",
                "timestamp": ack.ack_timestamp.isoformat(),
                "actor": ack.operator_name,
                "event_id": ack.id,
                "details": f"Alarm acknowledged after {ack.ack_delay_seconds:.1f}s delay. SLA Status: {ack.sla_status}. Notes: {ack.notes or 'None'}",
                "badge_color": "yellow" if ack.sla_status == "DELAYED" else "blue"
            })

    # 4. Incident Creation
    timeline.append({
        "stage": "Incident Inception",
        "timestamp": inc.created_timestamp.isoformat(),
        "actor": inc.assigned_investigator or "Safety Ingestion System",
        "event_id": inc.id,
        "details": f"Incident logged with {inc.severity} severity. Status: {inc.status}. Title: {inc.title}",
        "badge_color": "orange"
    })

    # 5, 6, 7. Corrective actions lifecycle
    for act in actions:
        # Assignment
        timeline.append({
            "stage": "Corrective Action Assigned",
            "timestamp": act.created_at.isoformat(),
            "actor": act.assigned_to,
            "event_id": act.id,
            "details": f"Action {act.id} assigned with {act.priority} priority. Title: {act.title}. Due date: {act.due_date.strftime('%Y-%m-%d')}",
            "badge_color": "purple"
        })

        # Completion
        if act.completed_at:
            timeline.append({
                "stage": "Action Completed",
                "timestamp": act.completed_at.isoformat(),
                "actor": act.assigned_to,
                "event_id": act.id,
                "details": f"Work order completed for {act.id}. Awaiting safety officer verification sign-off.",
                "badge_color": "emerald"
            })

        # Verification
        if act.is_verified and act.verified_at:
            timeline.append({
                "stage": "Safety Verification Sign-off",
                "timestamp": act.verified_at.isoformat(),
                "actor": act.verified_by or "Chief Safety Officer",
                "event_id": act.id,
                "details": f"Physical safety inspection verified. Notes: {act.verification_notes or 'Passed inspection'}",
                "badge_color": "emerald"
            })

    # 8. Incident Closure
    if inc.closed_timestamp:
        timeline.append({
            "stage": "Incident Closure",
            "timestamp": inc.closed_timestamp.isoformat(),
            "actor": inc.assigned_investigator or "Safety Officer",
            "event_id": inc.id,
            "details": f"Formal closure certified. All corrective verifications successfully completed.",
            "badge_color": "green"
        })

    # Sort timeline chronologically
    timeline.sort(key=lambda x: x["timestamp"])

    return {
        "incident": {
            "id": inc.id,
            "title": inc.title,
            "description": inc.description,
            "incident_type": inc.incident_type,
            "severity": inc.severity,
            "status": inc.status,
            "assigned_investigator": inc.assigned_investigator,
            "created_timestamp": inc.created_timestamp.isoformat(),
            "contained_timestamp": inc.contained_timestamp.isoformat() if inc.contained_timestamp else None,
            "resolved_timestamp": inc.resolved_timestamp.isoformat() if inc.resolved_timestamp else None,
            "closed_timestamp": inc.closed_timestamp.isoformat() if inc.closed_timestamp else None,
        },
        "plant": {
            "id": plant.id if plant else inc.plant_id,
            "name": plant.name if plant else inc.plant_id,
        },
        "machine": {
            "id": machine.id if machine else inc.machine_id,
            "name": machine.name if machine else inc.machine_id,
            "current_state": machine.current_state if machine else "UNKNOWN",
        },
        "safety_zone": {
            "id": zone.id,
            "name": zone.name,
            "hazard_level": zone.hazard_level,
        } if zone else None,
        "triggering_alarm": {
            "id": triggering_alarm.id,
            "severity": triggering_alarm.severity,
            "status": triggering_alarm.status,
            "event_timestamp": triggering_alarm.event_timestamp.isoformat(),
        } if triggering_alarm else None,
        "corrective_actions": [
            {
                "id": act.id,
                "title": act.title,
                "assigned_to": act.assigned_to,
                "priority": act.priority,
                "status": act.status,
                "due_date": act.due_date.isoformat(),
                "completed_at": act.completed_at.isoformat() if act.completed_at else None,
                "is_verified": act.is_verified,
                "verified_by": act.verified_by,
                "verified_at": act.verified_at.isoformat() if act.verified_at else None,
                "verification_notes": act.verification_notes,
            }
            for act in actions
        ],
        "timeline": timeline,
    }


@router.post("/{incident_id}/acknowledge")
def acknowledge_incident(
    incident_id: str,
    status: str = Body(..., embed=True),
    investigator: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    """Update incident operational status (e.g. from OPEN to INVESTIGATING or CONTAINED)."""
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    valid_statuses = ["OPEN", "INVESTIGATING", "CONTAINED", "RESOLVED", "CLOSED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    # Check rule: cannot close incident if any corrective action is unverified
    if status == "CLOSED":
        unverified_count = (
            db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.incident_id == incident_id,
                CorrectiveAction.is_verified == False
            )
            .count()
        )
        if unverified_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot close incident: {unverified_count} corrective actions are pending mandatory safety verification."
            )
        inc.closed_timestamp = datetime.utcnow()

    inc.status = status
    if investigator:
        inc.assigned_investigator = investigator

    # Log to audit log
    audit = AuditLog(
        entity_name="Incident",
        entity_id=inc.id,
        action="UPDATE_STATUS",
        actor=investigator or "Incident Responder",
        details=f"Incident {inc.id} transitioned to {status}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {"message": f"Incident {incident_id} successfully updated to {status}", "status": inc.status}
