from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from backend.app.database import get_db
from backend.app.models import CorrectiveAction, Incident, AuditLog
from generator.id_generator import IdGenerator

router = APIRouter(prefix="/corrective-actions", tags=["Corrective Actions"])


class CreateActionRequest(BaseModel):
    incident_id: str
    title: str
    description: Optional[str] = None
    assigned_to: str
    priority: str = "HIGH"
    due_date: datetime


class VerifyActionRequest(BaseModel):
    verified_by: str
    verification_notes: str


class UpdateActionStatusRequest(BaseModel):
    status: str
    actor: Optional[str] = "Operator"


@router.get("")
def list_corrective_actions(
    incident_id: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    is_verified: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(15, ge=1, le=100),
    sort_by: str = "due_date",
    sort_order: str = "asc",
    db: Session = Depends(get_db)
):
    """List corrective actions with filtering, verification state, and pagination."""
    query = db.query(CorrectiveAction)

    if incident_id:
        query = query.filter(CorrectiveAction.incident_id == incident_id)
    if status:
        query = query.filter(CorrectiveAction.status == status)
    if priority:
        query = query.filter(CorrectiveAction.priority == priority)
    if is_verified is not None:
        query = query.filter(CorrectiveAction.is_verified == is_verified)

    if search:
        search_filter = or_(
            CorrectiveAction.id.ilike(f"%{search}%"),
            CorrectiveAction.title.ilike(f"%{search}%"),
            CorrectiveAction.assigned_to.ilike(f"%{search}%"),
            CorrectiveAction.description.ilike(f"%{search}%"),
        )
        query = query.filter(search_filter)

    total = query.count()

    sort_col = getattr(CorrectiveAction, sort_by, CorrectiveAction.due_date)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_col.desc())
    else:
        query = query.order_by(sort_col.asc())

    actions = query.offset((page - 1) * page_size).limit(page_size).all()

    items = []
    for a in actions:
        items.append({
            "id": a.id,
            "incident_id": a.incident_id,
            "title": a.title,
            "description": a.description,
            "assigned_to": a.assigned_to,
            "priority": a.priority,
            "due_date": a.due_date.isoformat(),
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            "status": a.status,
            "verification_required": a.verification_required,
            "is_verified": a.is_verified,
            "verified_by": a.verified_by,
            "verified_at": a.verified_at.isoformat() if a.verified_at else None,
            "verification_notes": a.verification_notes,
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


@router.post("")
def create_corrective_action(payload: CreateActionRequest, db: Session = Depends(get_db)):
    """Create a new corrective action for an incident."""
    inc = db.query(Incident).filter(Incident.id == payload.incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    existing_count = db.query(CorrectiveAction).filter(CorrectiveAction.incident_id == payload.incident_id).count()
    act_id = IdGenerator.corrective_action_id(payload.incident_id, existing_count + 1)

    new_action = CorrectiveAction(
        id=act_id,
        incident_id=payload.incident_id,
        title=payload.title,
        description=payload.description,
        assigned_to=payload.assigned_to,
        priority=payload.priority,
        due_date=payload.due_date,
        status="PENDING",
        verification_required=True,
        is_verified=False,
        created_at=datetime.utcnow(),
    )
    db.add(new_action)

    audit = AuditLog(
        entity_name="CorrectiveAction",
        entity_id=act_id,
        action="CREATE",
        actor=payload.assigned_to,
        details=f"Created action {act_id} for incident {payload.incident_id}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {"message": "Corrective action created", "id": act_id}


@router.post("/{action_id}/verify")
def verify_corrective_action(action_id: str, payload: VerifyActionRequest, db: Session = Depends(get_db)):
    """Record safety officer verification and sign-off for a completed action."""
    action = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Corrective action not found")

    action.is_verified = True
    action.verified_by = payload.verified_by
    action.verified_at = datetime.utcnow()
    action.verification_notes = payload.verification_notes
    action.updated_at = datetime.utcnow()

    # If action was COMPLETED, we can now safely move it to CLOSED
    if action.status == "COMPLETED":
        action.status = "CLOSED"

    audit = AuditLog(
        entity_name="CorrectiveAction",
        entity_id=action.id,
        action="VERIFY",
        actor=payload.verified_by,
        details=f"Safety verification certified: {payload.verification_notes}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {
        "message": f"Action {action_id} successfully verified by {payload.verified_by}",
        "status": action.status,
        "is_verified": action.is_verified,
        "verified_at": action.verified_at.isoformat(),
    }


@router.put("/{action_id}/status")
def update_action_status(action_id: str, payload: UpdateActionStatusRequest, db: Session = Depends(get_db)):
    """
    Update action lifecycle state with strict safety enforcement:
    Business Rule: Cannot close or complete an action without required verification!
    """
    action = db.query(CorrectiveAction).filter(CorrectiveAction.id == action_id).first()
    if not action:
        raise HTTPException(status_code=404, detail="Corrective action not found")

    target_status = payload.status.upper()
    valid_statuses = ["PENDING", "IN_PROGRESS", "COMPLETED", "CLOSED", "CANCELLED"]
    if target_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of {valid_statuses}")

    # Enforce Business Rule: prevent closing action without required verification
    if target_status == "CLOSED" and action.verification_required and not action.is_verified:
        raise HTTPException(
            status_code=400,
            detail=f"Safety Policy Violation: Action {action_id} requires mandatory physical verification before formal closure."
        )

    action.status = target_status
    if target_status == "COMPLETED" and not action.completed_at:
        action.completed_at = datetime.utcnow()
    action.updated_at = datetime.utcnow()

    audit = AuditLog(
        entity_name="CorrectiveAction",
        entity_id=action.id,
        action="UPDATE_STATUS",
        actor=payload.actor or "Operator",
        details=f"Action {action.id} status changed to {target_status}",
        timestamp=datetime.utcnow()
    )
    db.add(audit)
    db.commit()

    return {"message": f"Action {action_id} status updated to {target_status}", "status": action.status}
