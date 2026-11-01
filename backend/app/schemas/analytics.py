from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel


class SafetyAnomalySchema(BaseModel):
    id: str
    machine_id: Optional[str] = None
    plant_id: Optional[str] = None
    anomaly_type: str
    severity: str
    detection_timestamp: datetime
    related_event_ids: Optional[str] = None
    explanation: str
    recommended_action: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class OverviewStatsSchema(BaseModel):
    total_plants: int
    total_machines: int
    total_alarms: int
    critical_alarms: int
    active_incidents: int
    unresolved_corrective_actions: int
    plant_safety_score: float
    data_integrity_score: float


class AlarmTrendPoint(BaseModel):
    date: str
    critical: int = 0
    high: int = 0
    medium: int = 0
    low: int = 0
    total: int = 0


class SeverityDistributionItem(BaseModel):
    severity: str
    count: int
    percentage: float


class UnsafeMachineItem(BaseModel):
    machine_id: str
    machine_name: str
    plant_id: str
    plant_name: str
    critical_alarms_count: int
    total_alarms_count: int
    incident_count: int
    current_state: str


class PlantSummaryItem(BaseModel):
    plant_id: str
    plant_name: str
    alarm_count: int
    critical_alarms: int
    incident_count: int
    safety_score: float
