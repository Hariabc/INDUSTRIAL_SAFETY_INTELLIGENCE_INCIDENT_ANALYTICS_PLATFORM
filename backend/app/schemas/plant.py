from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class SafetyZoneSchema(BaseModel):
    id: str
    plant_id: str
    name: str
    zone_type: str
    hazard_level: str
    max_occupancy: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlantSchema(BaseModel):
    id: str
    name: str
    location: str
    operational_status: str
    total_lines: int
    safety_score: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PlantDetailSchema(PlantSchema):
    machines_count: int = 0
    active_alarms_count: int = 0
    critical_incidents_count: int = 0
    safety_zones: List[SafetyZoneSchema] = []


class InterlockSchema(BaseModel):
    id: str
    machine_id: str
    name: str
    interlock_type: str
    target_state: str
    current_state: str
    is_safety_critical: bool
    bypass_allowed: bool
    last_tested_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class MachineSchema(BaseModel):
    id: str
    plant_id: str
    name: str
    type: str
    model_number: Optional[str] = None
    installation_date: datetime
    current_state: str
    criticality: str
    is_isolated: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MachineDetailSchema(MachineSchema):
    plant_name: Optional[str] = None
    safety_zones: List[SafetyZoneSchema] = []
    interlocks: List[InterlockSchema] = []
    alarm_count: int = 0
    incident_count: int = 0
    last_event_timestamp: Optional[datetime] = None
