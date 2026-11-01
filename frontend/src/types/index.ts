export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';

export type MachineState = 'RUNNING' | 'IDLE' | 'TRIPPED' | 'EMERGENCY_STOP' | 'MAINTENANCE' | 'UNSAFE';

export interface Plant {
  id: string;
  name: string;
  location: string;
  operational_status: string;
  total_lines: number;
  safety_score: number;
  created_at: string;
  updated_at: string;
  machines_count?: number;
  active_alarms_count?: number;
  critical_incidents_count?: number;
}

export interface SafetyZone {
  id: string;
  plant_id: string;
  name: string;
  zone_type: string;
  hazard_level: string;
  max_occupancy: number;
  coverage_type?: string;
}

export interface Interlock {
  id: string;
  machine_id: string;
  name: string;
  interlock_type: string;
  target_state: string;
  current_state: string;
  is_safety_critical: boolean;
  bypass_allowed: boolean;
  last_tested_at?: string;
}

export interface Machine {
  id: string;
  plant_id: string;
  plant_name?: string;
  name: string;
  type: string;
  model_number?: string;
  installation_date: string;
  current_state: MachineState;
  criticality: Severity;
  is_isolated: boolean;
  alarm_count?: number;
  incident_count?: number;
  last_event_timestamp?: string;
}

export interface MachineDetail {
  machine: Machine;
  stats: {
    total_alarms: number;
    critical_alarms: number;
    incidents: number;
  };
  interlocks: Interlock[];
  safety_zones: SafetyZone[];
}

export interface AlarmEvent {
  id: string;
  alarm_definition_id: string;
  machine_id: string;
  plant_id: string;
  severity: Severity;
  source_event_id: string;
  value?: number;
  threshold?: number;
  unit?: string;
  status: string;
  event_timestamp: string;
  cleared_timestamp?: string;
  is_nuisance: boolean;
}

export interface Acknowledgement {
  id: string;
  alarm_event_id: string;
  operator_name: string;
  operator_shift_id?: string;
  ack_timestamp: string;
  ack_delay_seconds: number;
  sla_status: 'WITHIN_SLA' | 'DELAYED' | 'ANOMALOUS_PRE_ALARM';
  notes?: string;
}

export interface Incident {
  id: string;
  plant_id: string;
  plant_name?: string;
  machine_id: string;
  machine_name?: string;
  safety_zone_id?: string;
  triggering_alarm_id?: string;
  title: string;
  description?: string;
  incident_type: string;
  severity: Severity;
  status: 'OPEN' | 'INVESTIGATING' | 'CONTAINED' | 'RESOLVED' | 'CLOSED';
  assigned_investigator?: string;
  created_timestamp: string;
  resolved_timestamp?: string;
  closed_timestamp?: string;
}

export interface TimelineItem {
  stage: string;
  timestamp: string;
  actor?: string;
  event_id?: string;
  details: string;
  badge_color?: string;
}

export interface IncidentDetail {
  incident: Incident;
  plant: { id: string; name: string };
  machine: { id: string; name: string; current_state: string };
  safety_zone?: { id: string; name: string; hazard_level: string };
  triggering_alarm?: { id: string; severity: string; status: string; event_timestamp: string };
  corrective_actions: CorrectiveAction[];
  timeline: TimelineItem[];
}

export interface CorrectiveAction {
  id: string;
  incident_id: string;
  title: string;
  description?: string;
  assigned_to: string;
  priority: Severity;
  due_date: string;
  completed_at?: string;
  status: 'PENDING' | 'IN_PROGRESS' | 'COMPLETED' | 'CLOSED' | 'CANCELLED';
  verification_required: boolean;
  is_verified: boolean;
  verified_by?: string;
  verified_at?: string;
  verification_notes?: string;
  created_at: string;
}

export interface SafetyAnomaly {
  id: string;
  machine_id?: string;
  machine_name?: string;
  plant_id?: string;
  plant_name?: string;
  anomaly_type: string;
  severity: Severity;
  detection_timestamp: string;
  related_event_ids: string[];
  explanation: string;
  recommended_action: string;
  status: string;
  created_at: string;
}

export interface OverviewStats {
  total_plants: number;
  total_machines: number;
  total_alarms: number;
  critical_alarms: number;
  active_incidents: number;
  unresolved_corrective_actions: number;
  plant_safety_score: number;
  data_integrity_score: number;
}

export interface ModelPerformance {
  true_positives: number;
  false_positives: number;
  true_negatives: number;
  false_negatives: number;
  precision: number;
  recall: number;
  f1_score: number;
  detection_coverage: number;
  ground_truth_total: number;
  total_detections: number;
}

export interface OperationalKPIs {
  total_alarms: number;
  critical_alarms: number;
  active_incidents: number;
  resolved_incidents: number;
  avg_acknowledgement_time_seconds: number;
  avg_incident_resolution_time_hours: number;
  delayed_acknowledgement_percentage: number;
  repeated_unsafe_machine_count: number;
  nuisance_alarm_percentage: number;
  corrective_action_verification_rate: number;
  data_integrity_score: number;
}

export interface EvaluationResponse {
  evaluation_timestamp: string;
  model_performance: ModelPerformance;
  operational_kpis: OperationalKPIs;
}

export interface PaginatedResult<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
