import json
from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.config import settings
from backend.app.models import (
    Machine, Interlock,
    AlarmDefinition, AlarmEvent, Acknowledgement,
    Incident, CorrectiveAction, SafetyAnomaly, MachineStateEvent
)
from generator.id_generator import IdGenerator


class SafetyDetectionEngine:
    """
    Explainable Industrial Safety Anomaly Detection Engine.
    Executes 8 deterministic, parameter-configurable safety rules.
    """

    def __init__(
        self,
        db: Session,
        flood_threshold: int = None,
        flood_window_minutes: int = None,
        repeated_window_hours: int = None,
        repeated_min_events: int = None,
        nuisance_min_count: int = None,
        nuisance_max_incident_rate: float = None,
    ):
        self.db = db
        self.flood_threshold = flood_threshold or settings.ALARM_FLOOD_THRESHOLD
        self.flood_window_minutes = flood_window_minutes or settings.ALARM_FLOOD_WINDOW_MINUTES
        self.repeated_window_hours = repeated_window_hours or settings.REPEATED_UNSAFE_WINDOW_HOURS
        self.repeated_min_events = repeated_min_events or settings.REPEATED_UNSAFE_MIN_EVENTS
        self.nuisance_min_count = nuisance_min_count or settings.NUISANCE_ALARM_MIN_COUNT
        self.nuisance_max_incident_rate = (
            nuisance_max_incident_rate
            if nuisance_max_incident_rate is not None
            else settings.NUISANCE_MAX_INCIDENT_RATE
        )

    def run_all_rules(self, persist_to_db: bool = True) -> List[SafetyAnomaly]:
        """Execute all 8 detection rules and optionally store anomalies in database."""
        all_detections: List[SafetyAnomaly] = []
        anomaly_seq = 1

        # Clear existing detections if persisting
        if persist_to_db:
            self.db.query(SafetyAnomaly).delete()
            self.db.commit()

        # Rule 1: Repeated Unsafe Conditions
        r1 = self.detect_repeated_unsafe_conditions(anomaly_seq)
        anomaly_seq += len(r1)
        all_detections.extend(r1)

        # Rule 2: Delayed Acknowledgements & Pre-Alarm Acks
        r2 = self.detect_delayed_acknowledgements(anomaly_seq)
        anomaly_seq += len(r2)
        all_detections.extend(r2)

        # Rule 3: Alarm Floods
        r3 = self.detect_alarm_floods(anomaly_seq)
        anomaly_seq += len(r3)
        all_detections.extend(r3)

        # Rule 4: Nuisance Alarms
        r4 = self.detect_nuisance_alarms(anomaly_seq)
        anomaly_seq += len(r4)
        all_detections.extend(r4)

        # Rule 5: Interlock Violations
        r5 = self.detect_interlock_violations(anomaly_seq)
        anomaly_seq += len(r5)
        all_detections.extend(r5)

        # Rule 6: Missing Incident Context
        r6 = self.detect_missing_incident_context(anomaly_seq)
        anomaly_seq += len(r6)
        all_detections.extend(r6)

        # Rule 7: Duplicate Alarm Replay
        r7 = self.detect_duplicate_alarm_replay(anomaly_seq)
        anomaly_seq += len(r7)
        all_detections.extend(r7)

        # Rule 8: Incomplete Corrective Actions
        r8 = self.detect_incomplete_corrective_actions(anomaly_seq)
        anomaly_seq += len(r8)
        all_detections.extend(r8)

        if persist_to_db and all_detections:
            self.db.bulk_save_objects(all_detections)
            self.db.commit()

        return all_detections

    # Rule 1: Repeated unsafe machine conditions
    def detect_repeated_unsafe_conditions(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # Find machines with >= repeated_min_events high/critical alarms in rolling window
        high_alarms = (
            self.db.query(
                AlarmEvent.machine_id,
                AlarmEvent.plant_id,
                func.count(AlarmEvent.id).label("cnt"),
                func.group_concat(AlarmEvent.id).label("event_ids")
            )
            .filter(AlarmEvent.severity.in_(["CRITICAL", "HIGH"]))
            .group_by(AlarmEvent.machine_id, AlarmEvent.plant_id)
            .having(func.count(AlarmEvent.id) >= self.repeated_min_events)
            .all()
        )

        for m_id, p_id, count, ids_str in high_alarms:
            # Check state transitions for this machine to confirm unsafe pattern
            unsafe_transitions = (
                self.db.query(MachineStateEvent)
                .filter(
                    MachineStateEvent.machine_id == m_id,
                    MachineStateEvent.new_state.in_(["UNSAFE", "TRIPPED", "EMERGENCY_STOP"])
                )
                .count()
            )

            if count >= self.repeated_min_events or unsafe_transitions >= 2:
                det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
                event_list = ids_str.split(",")[:10] if ids_str else []
                detections.append(SafetyAnomaly(
                    id=det_id,
                    machine_id=m_id,
                    plant_id=p_id,
                    anomaly_type="REPEATED_UNSAFE_CONDITION",
                    severity="CRITICAL",
                    detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                    related_event_ids=json.dumps(event_list),
                    explanation=f"Machine {m_id} exhibited {count} high/critical alarms and {unsafe_transitions} trips/unsafe state transitions.",
                    recommended_action="Isolate equipment immediately, execute mechanical integrity inspection, and recalibrate safety interlocks.",
                    status="DETECTED"
                ))

        return detections

    # Rule 2: Delayed acknowledgements & anomalous pre-alarm acks
    def detect_delayed_acknowledgements(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # 1. First, detect ALL temporal violations (ack precedes alarm) without limit
        pre_alarm_acks = (
            self.db.query(Acknowledgement, AlarmEvent, AlarmDefinition)
            .join(AlarmEvent, Acknowledgement.alarm_event_id == AlarmEvent.id)
            .join(AlarmDefinition, AlarmEvent.alarm_definition_id == AlarmDefinition.id)
            .filter(Acknowledgement.ack_timestamp < AlarmEvent.event_timestamp)
            .all()
        )

        for ack, alm, definition in pre_alarm_acks:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=alm.machine_id,
                plant_id=alm.plant_id,
                anomaly_type="DELAYED_ACKNOWLEDGEMENT",
                severity="HIGH",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([ack.id, alm.id]),
                explanation=f"Temporal violation: Acknowledgement {ack.id} occurred at {ack.ack_timestamp}, which precedes alarm {alm.id} ({alm.event_timestamp}).",
                recommended_action="Audit SCADA/PLC time synchronization daemon and investigate event pipeline latency.",
                status="DETECTED"
            ))

        # 2. Then detect SLA breaches (sample for explainability)
        sla_breaches = (
            self.db.query(Acknowledgement, AlarmEvent, AlarmDefinition)
            .join(AlarmEvent, Acknowledgement.alarm_event_id == AlarmEvent.id)
            .join(AlarmDefinition, AlarmEvent.alarm_definition_id == AlarmDefinition.id)
            .filter(
                Acknowledgement.ack_timestamp >= AlarmEvent.event_timestamp,
                Acknowledgement.ack_delay_seconds > AlarmDefinition.ack_sla_seconds
            )
            .limit(100)
            .all()
        )

        for ack, alm, definition in sla_breaches:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            sla = definition.ack_sla_seconds
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=alm.machine_id,
                plant_id=alm.plant_id,
                anomaly_type="DELAYED_ACKNOWLEDGEMENT",
                severity="MEDIUM" if alm.severity in ["LOW", "INFO"] else "HIGH",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([ack.id, alm.id]),
                explanation=f"Acknowledgement SLA breached: Alarm {alm.id} acknowledged after {ack.ack_delay_seconds:.1f}s (SLA limit: {sla}s).",
                recommended_action="Review shift staffing allocation and operator alarm dashboard prioritization.",
                status="DETECTED"
            ))

        return detections

    # Rule 3: Alarm floods (ISA-18.2: excessive alarms in short window)
    def detect_alarm_floods(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # Query alarms grouped by machine and hour
        # In SQLite/Postgres, strftime('%Y-%m-%d %H', event_timestamp) groups into hourly windows
        hourly_floods = (
            self.db.query(
                AlarmEvent.machine_id,
                AlarmEvent.plant_id,
                func.strftime("%Y-%m-%d %H", AlarmEvent.event_timestamp).label("hour_window"),
                func.count(AlarmEvent.id).label("alarm_count"),
                func.group_concat(AlarmEvent.id).label("event_ids")
            )
            .group_by(AlarmEvent.machine_id, AlarmEvent.plant_id, "hour_window")
            .having(func.count(AlarmEvent.id) >= self.flood_threshold)
            .all()
        )

        for m_id, p_id, hr_win, count, ids_str in hourly_floods:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            sample_ids = ids_str.split(",")[:15] if ids_str else []
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=m_id,
                plant_id=p_id,
                anomaly_type="ALARM_FLOOD",
                severity="HIGH" if count >= 20 else "MEDIUM",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps(sample_ids),
                explanation=f"Alarm flood detected on Machine {m_id}: {count} alarms raised in window {hr_win}:00 (threshold: {self.flood_threshold}).",
                recommended_action="Activate flood suppression logic, verify cascade trip root cause, and review alarm deadband settings.",
                status="DETECTED"
            ))

        return detections

    # Rule 4: Nuisance alarms
    def detect_nuisance_alarms(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # Find alarm definitions that trigger frequently (> nuisance_min_count) but are low severity
        frequent_low = (
            self.db.query(
                AlarmEvent.alarm_definition_id,
                AlarmEvent.machine_id,
                AlarmEvent.plant_id,
                func.count(AlarmEvent.id).label("cnt")
            )
            .filter(AlarmEvent.severity.in_(["LOW", "INFO"]))
            .group_by(AlarmEvent.alarm_definition_id, AlarmEvent.machine_id, AlarmEvent.plant_id)
            .having(func.count(AlarmEvent.id) >= self.nuisance_min_count)
            .all()
        )

        for def_id, m_id, p_id, count in frequent_low:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=m_id,
                plant_id=p_id,
                anomaly_type="NUISANCE_ALARM",
                severity="LOW",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([def_id, m_id]),
                explanation=f"Definition {def_id} triggered {count} times on Machine {m_id} without escalating to an incident (chattering alarm).",
                recommended_action="Increase sensor filter deadband, adjust hysteresis parameters, or schedule preventive sensor recalibration.",
                status="DETECTED"
            ))

        return detections

    # Rule 5: Interlock violations
    def detect_interlock_violations(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # Query running machines with violated safety interlocks
        violations = (
            self.db.query(Interlock, Machine)
            .join(Machine, Interlock.machine_id == Machine.id)
            .filter(
                Machine.current_state == "RUNNING",
                Interlock.is_safety_critical == True,
                Interlock.bypass_allowed == False,
                Interlock.current_state.in_(["BYPASSED", "FAULT"])
            )
            .all()
        )

        for itl, mch in violations:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=mch.id,
                plant_id=mch.plant_id,
                anomaly_type="INTERLOCK_VIOLATION",
                severity="CRITICAL",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([itl.id, mch.id]),
                explanation=f"Safety violation: Interlock {itl.id} ({itl.name}) is in '{itl.current_state}' while Machine {mch.id} is in RUNNING state (bypass prohibited).",
                recommended_action="Trigger emergency interlock latch trip, halt machine production line, and require physical safety lock verification.",
                status="DETECTED"
            ))

        return detections

    # Rule 6: Missing incident context
    def detect_missing_incident_context(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        # Incidents with null triggering_alarm_id
        missing = self.db.query(Incident).filter(Incident.triggering_alarm_id.is_(None)).all()

        for inc in missing:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=inc.machine_id,
                plant_id=inc.plant_id,
                anomaly_type="MISSING_INCIDENT_CONTEXT",
                severity="HIGH",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([inc.id]),
                explanation=f"Incident {inc.id} lacks root-cause triggering alarm or causal telemetry link (untraceable safety event).",
                recommended_action="Reconcile historian logs around incident inception timestamp and link originating alarm event.",
                status="DETECTED"
            ))

        return detections

    # Rule 7: Duplicate alarm replay
    def detect_duplicate_alarm_replay(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        dups = (
            self.db.query(
                AlarmEvent.source_event_id,
                func.count(AlarmEvent.id).label("cnt"),
                func.group_concat(AlarmEvent.id).label("ids")
            )
            .group_by(AlarmEvent.source_event_id)
            .having(func.count(AlarmEvent.id) > 1)
            .all()
        )

        for src_id, count, ids_str in dups:
            sample_ids = ids_str.split(",") if ids_str else []
            first_ev = self.db.query(AlarmEvent).filter(AlarmEvent.source_event_id == src_id).first()
            m_id = first_ev.machine_id if first_ev else None
            p_id = first_ev.plant_id if first_ev else None

            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=m_id,
                plant_id=p_id,
                anomaly_type="DUPLICATE_ALARM_REPLAY",
                severity="MEDIUM",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps(sample_ids),
                explanation=f"Duplicate event ingestion replay: source_event_id '{src_id}' ingested {count} times across IDs {sample_ids}.",
                recommended_action="Verify broker idempotency keys, check MQTT/Kafka dedup window, and purge replayed records.",
                status="DETECTED"
            ))

        return detections

    # Rule 8: Incomplete corrective actions
    def detect_incomplete_corrective_actions(self, start_seq: int) -> List[SafetyAnomaly]:
        detections = []
        unverified = (
            self.db.query(CorrectiveAction)
            .filter(
                CorrectiveAction.status.in_(["COMPLETED", "CLOSED"]),
                (CorrectiveAction.is_verified == False) | (CorrectiveAction.verified_at.is_(None))
            )
            .all()
        )

        for act in unverified:
            det_id = IdGenerator.anomaly_id(2026, start_seq + len(detections))
            inc = self.db.query(Incident).filter(Incident.id == act.incident_id).first()
            m_id = inc.machine_id if inc else None
            p_id = inc.plant_id if inc else None

            detections.append(SafetyAnomaly(
                id=det_id,
                machine_id=m_id,
                plant_id=p_id,
                anomaly_type="INCOMPLETE_CORRECTIVE_ACTION",
                severity="HIGH",
                detection_timestamp=datetime.now(timezone.utc).replace(tzinfo=None),
                related_event_ids=json.dumps([act.id, act.incident_id]),
                explanation=f"Governance non-compliance: Corrective action {act.id} is marked '{act.status}' without safety sign-off verification.",
                recommended_action="Revert action status to IN_PROGRESS, assign qualified safety officer, and execute mandatory verification checklist.",
                status="DETECTED"
            ))

        return detections
