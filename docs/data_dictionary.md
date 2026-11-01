# Data Dictionary: Industrial Safety Intelligence Platform

This document describes all entities, fields, data types, constraints, allowed enumerations, and relationships in the platform database.

---

## 1. plants
Represents manufacturing plants within the enterprise.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Plant ID (e.g., `PLN-001`) |
| `name` | VARCHAR(200) | No | No | - | Human-readable plant name |
| `location` | VARCHAR(200) | No | No | - | Geographic location / campus |
| `operational_status` | VARCHAR(50) | No | No | - | `ACTIVE`, `MAINTENANCE`, `OFFLINE` |
| `total_lines` | INTEGER | No | No | - | Number of production lines |
| `safety_score` | FLOAT | No | No | - | Rolling plant safety score (0.0 to 100.0) |
| `created_at` | TIMESTAMP | No | No | - | Record creation timestamp (UTC) |
| `updated_at` | TIMESTAMP | No | No | - | Record modification timestamp (UTC) |

---

## 2. machines
Industrial machinery monitored for telemetry, safety state, and alarm events.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Machine ID (e.g., `MCH-001`) |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Associated plant |
| `name` | VARCHAR(200) | No | No | - | Equipment asset name |
| `type` | VARCHAR(50) | No | No | - | `TURBINE`, `ROBOTIC_ARM`, `HYDRAULIC_PRESS`, `CONVEYOR`, `COMPRESSOR`, `REACTOR`, `CNC_MILL` |
| `model_number` | VARCHAR(100) | Yes | No | - | OEM model / serial spec |
| `installation_date` | TIMESTAMP | No | No | - | Commissioning date |
| `current_state` | VARCHAR(50) | No | No | - | `RUNNING`, `IDLE`, `TRIPPED`, `EMERGENCY_STOP`, `MAINTENANCE`, `UNSAFE` |
| `criticality` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `is_isolated` | BOOLEAN | No | No | - | Physical energy lockout/tagout isolation flag |
| `created_at` | TIMESTAMP | No | No | - | Timestamp created |
| `updated_at` | TIMESTAMP | No | No | - | Timestamp updated |

---

## 3. safety_zones
Designated containment and safety boundaries within a plant.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Safety Zone ID (`SAFE-PLN-001-001`) |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Plant ID |
| `name` | VARCHAR(200) | No | No | - | Zone name (e.g., Robot Enclosure Zone A) |
| `zone_type` | VARCHAR(50) | No | No | - | `HAZARDOUS`, `EXCLUSION`, `CONTROLLED`, `GENERAL` |
| `hazard_level` | VARCHAR(50) | No | No | - | `HIGH`, `MEDIUM`, `LOW` |
| `max_occupancy` | INTEGER | No | No | - | Permitted personnel limit |
| `created_at` | TIMESTAMP | No | No | - | Timestamp created |

---

## 4. machine_safety_zones
Bridge table mapping machines to one or more safety zones.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | INTEGER | No | Yes (Auto) | - | Surrogate primary key |
| `machine_id` | VARCHAR(50) | No | No | `machines.id` | Referenced machine |
| `safety_zone_id` | VARCHAR(50) | No | No | `safety_zones.id`| Referenced safety zone |
| `coverage_type` | VARCHAR(50) | No | No | - | `PRIMARY`, `SECONDARY` |
| `created_at` | TIMESTAMP | No | No | - | Timestamp mapped |

---

## 5. interlocks
Safety interlocks protecting personnel and equipment.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic ID (`ITL-MCH-001-001`) |
| `machine_id` | VARCHAR(50) | No | No | `machines.id` | Parent machine |
| `name` | VARCHAR(200) | No | No | - | Interlock designation |
| `interlock_type`| VARCHAR(50) | No | No | - | `HARDWARE_GUARD`, `PRESSURE_RELIEF`, `E_STOP_CIRCUIT`, `THERMAL_CUTOFF`, `LIGHT_CURTAIN` |
| `target_state` | VARCHAR(50) | No | No | - | Safe state: `ENGAGED`, `DISENGAGED` |
| `current_state` | VARCHAR(50) | No | No | - | Observed state: `ENGAGED`, `DISENGAGED`, `BYPASSED`, `FAULT` |
| `is_safety_critical`| BOOLEAN | No | No | - | Flag indicating fail-safe criticality |
| `bypass_allowed`| BOOLEAN | No | No | - | Whether administrative bypass is permitted |
| `last_tested_at`| TIMESTAMP | No | No | - | Interlock test verification date |
| `created_at` | TIMESTAMP | No | No | - | Record creation timestamp |
| `updated_at` | TIMESTAMP | No | No | - | Record update timestamp |

---

## 6. alarm_definitions
Master catalog of alarm specifications, severity levels, and acknowledgement SLAs.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic ID (e.g. `DEF-001`) |
| `code` | VARCHAR(50) | No | No | - | Unique alarm code (e.g. `ALM-CODE-001`) |
| `name` | VARCHAR(200) | No | No | - | Standard alarm name |
| `description` | VARCHAR(500) | Yes | No | - | Alarm trigger description |
| `severity` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| `category` | VARCHAR(100) | No | No | - | `SAFETY_INTERLOCK`, `OVERHEATING`, `PRESSURE_ANOMALY`, `VIBRATION`, `EMERGENCY_SHUTDOWN`, `TOXIC_GAS`, `ELECTRICAL_FAULT` |
| `ack_sla_seconds`| INTEGER | No | No | - | Mandatory SLA for acknowledgement (e.g., 300s, 900s, 1800s, 3600s) |
| `requires_clearance`| BOOLEAN | No | No | - | If operator clear action is mandatory |
| `created_at` | TIMESTAMP | No | No | - | Record creation timestamp |

---

## 7. operator_shifts
Industrial shift schedules and supervisory staffing logs.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Shift ID (`SHF-000001`) |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Plant ID |
| `shift_name` | VARCHAR(50) | No | No | - | `MORNING`, `AFTERNOON`, `NIGHT` |
| `lead_operator_name`| VARCHAR(100)| No | No | - | Lead operator on duty |
| `shift_start` | TIMESTAMP | No | No | - | Start of shift |
| `shift_end` | TIMESTAMP | No | No | - | End of shift |
| `created_at` | TIMESTAMP | No | No | - | Record creation timestamp |

---

## 8. machine_state_events
Historical, append-only log of machine state transitions. Historical state is never overwritten.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | INTEGER | No | Yes (Auto) | - | Event sequence ID |
| `machine_id` | VARCHAR(50) | No | No | `machines.id` | Target machine |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Target plant |
| `previous_state`| VARCHAR(50) | Yes | No | - | Machine state prior to event |
| `new_state` | VARCHAR(50) | No | No | - | `RUNNING`, `IDLE`, `TRIPPED`, `EMERGENCY_STOP`, `MAINTENANCE`, `UNSAFE` |
| `reason` | VARCHAR(255) | Yes | No | - | Reason / trigger for state change |
| `operator_shift_id`| VARCHAR(50)| Yes | No | `operator_shifts.id`| Active shift |
| `timestamp` | TIMESTAMP | No | No | - | Transition timestamp (UTC) |

---

## 9. alarm_events
Time-series log of raised industrial alarms with severity and source event tracking.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Alarm ID (`ALM-MCH-001-000001`) |
| `alarm_definition_id`| VARCHAR(50)| No | No | `alarm_definitions.id`| Catalog definition |
| `machine_id` | VARCHAR(50) | No | No | `machines.id` | Equipment asset |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Manufacturing plant |
| `severity` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW`, `INFO` |
| `source_event_id`| VARCHAR(100)| No | No | - | Ingestion raw event fingerprint |
| `value` | FLOAT | Yes | No | - | Recorded telemetry metric |
| `threshold` | FLOAT | Yes | No | - | Safety trigger limit |
| `unit` | VARCHAR(20) | Yes | No | - | Engineering units (°C, bar, mm/s, rpm) |
| `status` | VARCHAR(50) | No | No | - | `ACTIVE`, `ACKNOWLEDGED`, `CLEARED`, `SUPPRESSED` |
| `event_timestamp`| TIMESTAMP | No | No | - | Timestamp alarm occurred |
| `cleared_timestamp`| TIMESTAMP| Yes | No | - | Timestamp alarm returned to normal |
| `is_nuisance` | BOOLEAN | No | No | - | Flagged as nuisance / chattering alarm |
| `created_at` | TIMESTAMP | No | No | - | Ingestion timestamp |

---

## 10. acknowledgements
Operator confirmation of alarm awareness with delay and SLA compliance tracking.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic ACK ID (`ACK-ALM-...-01`) |
| `alarm_event_id`| VARCHAR(50)| No | No | `alarm_events.id` | Target alarm event |
| `operator_name`| VARCHAR(100)| No | No | - | Responding operator name |
| `operator_shift_id`| VARCHAR(50)| Yes | No | `operator_shifts.id`| Operational shift |
| `ack_timestamp`| TIMESTAMP | No | No | - | Time operator acknowledged alarm |
| `ack_delay_seconds`| FLOAT | No | No | - | `ack_timestamp - alarm_timestamp` |
| `sla_status` | VARCHAR(50) | No | No | - | `WITHIN_SLA`, `DELAYED`, `ANOMALOUS_PRE_ALARM` |
| `notes` | VARCHAR(500) | Yes | No | - | Operator commentary |
| `created_at` | TIMESTAMP | No | No | - | Record creation timestamp |

---

## 11. incidents
Safety incidents, near-misses, and interlock trips requiring containment and root-cause analysis.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Incident ID (`INC-2026-000001`) |
| `plant_id` | VARCHAR(50) | No | No | `plants.id` | Plant ID |
| `machine_id` | VARCHAR(50) | No | No | `machines.id` | Equipment involved |
| `safety_zone_id`| VARCHAR(50)| Yes | No | `safety_zones.id`| Zone affected |
| `triggering_alarm_id`| VARCHAR(50)| Yes | No | `alarm_events.id`| Alarm that precipitated incident |
| `title` | VARCHAR(255) | No | No | - | Incident title summary |
| `description` | VARCHAR(1000)| Yes | No | - | Detailed description |
| `incident_type`| VARCHAR(50) | No | No | - | `NEAR_MISS`, `EQUIPMENT_DAMAGE`, `SAFETY_BREACH`, `HAZARDOUS_RELEASE`, `INTERLOCK_FAILURE` |
| `severity` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `status` | VARCHAR(50) | No | No | - | `OPEN`, `INVESTIGATING`, `CONTAINED`, `RESOLVED`, `CLOSED` |
| `assigned_investigator`| VARCHAR(100)| Yes | No | - | Investigator name |
| `operator_shift_id`| VARCHAR(50)| Yes | No | `operator_shifts.id`| Shift during occurrence |
| `created_timestamp`| TIMESTAMP| No | No | - | Incident inception timestamp |
| `contained_timestamp`| TIMESTAMP| Yes| No | - | Containment timestamp |
| `resolved_timestamp`| TIMESTAMP| Yes| No | - | Corrective action resolution timestamp |
| `closed_timestamp`| TIMESTAMP| Yes| No | - | Formal closure timestamp |

---

## 12. incident_alarm_events
Bridge table linking multiple associated alarms to an incident investigation.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | INTEGER | No | Yes (Auto) | - | Link sequence ID |
| `incident_id` | VARCHAR(50) | No | No | `incidents.id` | Parent incident |
| `alarm_event_id`| VARCHAR(50)| No | No | `alarm_events.id` | Correlated alarm |
| `relationship_type`| VARCHAR(50)| No | No | - | `TRIGGER`, `CONSEQUENTIAL`, `CORRELATED` |
| `created_at` | TIMESTAMP | No | No | - | Timestamp linked |

---

## 13. corrective_actions
Action plans assigned to resolve safety hazards and prevent incident recurrence.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Action ID (`ACT-INC-2026-000001-01`) |
| `incident_id` | VARCHAR(50) | No | No | `incidents.id` | Source incident |
| `title` | VARCHAR(255) | No | No | - | Action title |
| `description` | VARCHAR(1000)| Yes | No | - | Detailed corrective procedure |
| `assigned_to` | VARCHAR(100) | No | No | - | Assigned engineer/technician |
| `priority` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `due_date` | TIMESTAMP | No | No | - | SLA due date |
| `completed_at` | TIMESTAMP | Yes | No | - | Completion timestamp |
| `status` | VARCHAR(50) | No | No | - | `PENDING`, `IN_PROGRESS`, `COMPLETED`, `CLOSED`, `CANCELLED` |
| `verification_required`| BOOLEAN| No | No | - | Flag indicating required safety verification |
| `is_verified` | BOOLEAN | No | No | - | Whether safety verification has succeeded |
| `verified_by` | VARCHAR(100) | Yes | No | - | Verifying safety officer |
| `verified_at` | TIMESTAMP | Yes | No | - | Verification timestamp |
| `verification_notes`| VARCHAR(500)| Yes| No | - | Verification evaluation remarks |
| `created_at` | TIMESTAMP | No | No | - | Record created |
| `updated_at` | TIMESTAMP | No | No | - | Record updated |

---

## 14. safety_anomalies
Explainable safety findings produced by the intelligence engine.

| Field | Data Type | Nullable | Primary Key | Foreign Key | Allowed Values / Description |
|---|---|---|---|---|---|
| `id` | VARCHAR(50) | No | Yes | - | Deterministic Anomaly ID (`ANM-2026-000001`) |
| `machine_id` | VARCHAR(50) | Yes | No | `machines.id` | Machine subject to anomaly |
| `plant_id` | VARCHAR(50) | Yes | No | `plants.id` | Plant subject to anomaly |
| `anomaly_type` | VARCHAR(100) | No | No | - | One of 8 detection rules |
| `severity` | VARCHAR(50) | No | No | - | `CRITICAL`, `HIGH`, `MEDIUM`, `LOW` |
| `detection_timestamp`| TIMESTAMP| No | No | - | Time detection executed |
| `related_event_ids`| TEXT | Yes | No | - | Comma-separated list or JSON IDs |
| `explanation` | TEXT | No | No | - | Human-understandable rationale |
| `recommended_action`| TEXT | No | No | - | Standard operating recommendation |
| `status` | VARCHAR(50) | No | No | - | `DETECTED`, `INVESTIGATING`, `CONFIRMED`, `DISMISSED` |
| `created_at` | TIMESTAMP | No | No | - | Ingestion timestamp |

---

## 15. audit_logs & system_configs
Security, compliance, configuration, and SLA thresholds.
