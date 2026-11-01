from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


class AlarmDefinitionSchema(BaseModel):
    id: str
    code: str
    name: str
    description: Optional[str] = None
    severity: str
    category: str
    ack_sla_seconds: int
    requires_clearance: bool

    class Config:
        from_attributes = True


class AcknowledgementSchema(BaseModel):
    id: str
    alarm_event_id: str
    operator_name: str
    operator_shift_id: Optional[str] = None
    ack_timestamp: datetime
    ack_delay_seconds: float
    sla_status: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True


class AlarmEventSchema(BaseModel):
    id: str
    alarm_definition_id: str
    machine_id: str
    plant_id: str
    severity: str
    source_event_id: str
    value: Optional[float] = None
    threshold: Optional[float] = None
    unit: Optional[str] = None
    status: str
    event_timestamp: datetime
    cleared_timestamp: Optional[datetime] = None
    is_nuisance: bool

    class Config:
        from_attributes = True


class AlarmEventDetailSchema(AlarmEventSchema):
    definition_name: Optional[str] = None
    machine_name: Optional[str] = None
    plant_name: Optional[str] = None
    acknowledgement: Optional[AcknowledgementSchema] = None


class CorrectiveActionSchema(BaseModel):
    id: str
    incident_id: str
    title: str
    description: Optional[str] = None
    assigned_to: str
    priority: str
    due_date: datetime
    completed_at: Optional[datetime] = None
    status: str
    verification_required: bool
    is_verified: bool
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class IncidentSchema(BaseModel):
    id: str
    plant_id: str
    machine_id: str
    safety_zone_id: Optional[str] = None
    triggering_alarm_id: Optional[str] = None
    title: str
    description: Optional[str] = None
    incident_type: str
    severity: str
    status: str
    assigned_investigator: Optional[str] = None
    created_timestamp: datetime
    contained_timestamp: Optional[datetime] = None
    resolved_timestamp: Optional[datetime] = None
    closed_timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


class IncidentTimelineItem(BaseModel):
    timestamp: datetime
    stage: str
    actor: Optional[str] = None
    details: str
    event_id: Optional[str] = None


class IncidentDetailSchema(IncidentSchema):
    machine_name: Optional[str] = None
    plant_name: Optional[str] = None
    safety_zone_name: Optional[str] = None
    triggering_alarm: Optional[AlarmEventSchema] = None
    corrective_actions: List[CorrectiveActionSchema] = []
    timeline: List[IncidentTimelineItem] = []
