from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Any
import copy
import random
from generator.id_generator import IdGenerator


def inject_anomalies(
    alarm_events: List[dict],
    acknowledgements: List[dict],
    machines: List[dict],
    interlocks: List[dict],
    incidents: List[dict],
    corrective_actions: List[dict],
    config: Any,
    rng: random.Random
) -> Tuple[List[dict], Dict[str, Any]]:
    """
    Deliberately inject 5 designated anomaly edge-cases and record ground truth labels separately.
    
    Injected Anomaly Scenarios:
    A. ACK_BEFORE_ALARM: Acknowledgement timestamp precedes corresponding alarm event.
    B. IMPOSSIBLE_INTERLOCK_STATE: Critical interlock bypassed or faulted while machine is running.
    C. MISSING_INCIDENT_CONTEXT: Incident created without valid triggering alarm reference.
    D. DUPLICATE_ALARM_REPLAY: Duplicate alarm records generated from replayed source event.
    E. ACTION_CLOSED_WITHOUT_VERIFICATION: Corrective action marked completed/closed without verification.
    """
    ground_truth_records = []
    anomaly_counter = 1

    # Map alarms by ID
    alarm_map = {ev["id"]: ev for ev in alarm_events}

    # Scenario A: Acknowledgement before alarm
    # Select acknowledgements and alter ack_timestamp to be 60 to 300 seconds BEFORE alarm event timestamp
    ack_targets = [ack for ack in acknowledgements if ack["alarm_event_id"] in alarm_map]
    num_a = min(config.num_ack_before_alarm, len(ack_targets))
    selected_acks = rng.sample(ack_targets, num_a)

    for ack in selected_acks:
        alm = alarm_map[ack["alarm_event_id"]]
        alarm_time = alm["event_timestamp"]
        # Set ack time prior to alarm
        prior_delta = rng.uniform(60, 300)
        ack["ack_timestamp"] = alarm_time - timedelta(seconds=prior_delta)
        ack["ack_delay_seconds"] = round(-prior_delta, 2)
        ack["sla_status"] = "ANOMALOUS_PRE_ALARM"

        gt_id = IdGenerator.anomaly_id(2026, anomaly_counter)
        anomaly_counter += 1
        ground_truth_records.append({
            "anomaly_id": gt_id,
            "anomaly_type": "DELAYED_ACKNOWLEDGEMENT",
            "subtype": "ACK_BEFORE_ALARM",
            "entity_type": "acknowledgement",
            "entity_id": ack["id"],
            "machine_id": alm["machine_id"],
            "plant_id": alm["plant_id"],
            "timestamp": ack["ack_timestamp"].isoformat(),
            "details": f"Acknowledgement timestamp {ack['ack_timestamp']} strictly precedes alarm timestamp {alarm_time} by {prior_delta:.1f}s."
        })

    # Scenario B: Impossible interlock state
    # Machine in RUNNING state while safety-critical interlock is in FAULT or BYPASSED state with bypass_allowed=False
    running_machines = [m for m in machines if m["current_state"] == "RUNNING"]
    mch_itls = {}
    for itl in interlocks:
        mch_itls.setdefault(itl["machine_id"], []).append(itl)

    eligible_itls = []
    for rm in running_machines:
        for itl in mch_itls.get(rm["id"], []):
            if itl["is_safety_critical"] and not itl["bypass_allowed"]:
                eligible_itls.append((rm, itl))

    num_b = min(config.num_impossible_interlock, len(eligible_itls))
    selected_b = rng.sample(eligible_itls, num_b)

    for rm, itl in selected_b:
        illegal_state = rng.choice(["BYPASSED", "FAULT"])
        itl["current_state"] = illegal_state
        itl["updated_at"] = config.start_date + timedelta(days=rng.randint(5, 25))

        gt_id = IdGenerator.anomaly_id(2026, anomaly_counter)
        anomaly_counter += 1
        ground_truth_records.append({
            "anomaly_id": gt_id,
            "anomaly_type": "INTERLOCK_VIOLATION",
            "subtype": "IMPOSSIBLE_INTERLOCK_STATE",
            "entity_type": "interlock",
            "entity_id": itl["id"],
            "machine_id": rm["id"],
            "plant_id": rm["plant_id"],
            "timestamp": itl["updated_at"].isoformat(),
            "details": f"Machine {rm['id']} is RUNNING while safety-critical interlock {itl['id']} is in illegal state '{illegal_state}' (bypass prohibited)."
        })

    # Scenario C: Missing triggering context in incident
    # Remove triggering_alarm_id from selected incidents
    num_c = min(config.num_missing_incident_context, len(incidents))
    selected_c = rng.sample(incidents, num_c)

    for inc in selected_c:
        orig_trigger = inc["triggering_alarm_id"]
        inc["triggering_alarm_id"] = None
        inc["description"] += " [WARN: Ingestion error: Root triggering alarm link missing in telemetry ingestion]."

        gt_id = IdGenerator.anomaly_id(2026, anomaly_counter)
        anomaly_counter += 1
        ground_truth_records.append({
            "anomaly_id": gt_id,
            "anomaly_type": "MISSING_INCIDENT_CONTEXT",
            "subtype": "MISSING_TRIGGERING_ALARM",
            "entity_type": "incident",
            "entity_id": inc["id"],
            "machine_id": inc["machine_id"],
            "plant_id": inc["plant_id"],
            "timestamp": inc["created_timestamp"].isoformat(),
            "details": f"Incident {inc['id']} has no associated triggering alarm or causal event context."
        })

    # Scenario D: Duplicate alarm replay
    # Pick alarm events and duplicate them with the exact same source_event_id and timestamp
    num_d = min(config.num_duplicate_alarm_replay, len(alarm_events))
    sample_for_replay = rng.sample(alarm_events[:1000], num_d)
    replayed_events = []

    for orig_ev in sample_for_replay:
        # Create a cloned event with new primary key but identical source_event_id, machine_id, and timestamp
        dup_ev = copy.deepcopy(orig_ev)
        dup_ev["id"] = f"{orig_ev['id']}-DUP"
        # Duplicate timestamp and identical source event ID
        replayed_events.append(dup_ev)

        gt_id = IdGenerator.anomaly_id(2026, anomaly_counter)
        anomaly_counter += 1
        ground_truth_records.append({
            "anomaly_id": gt_id,
            "anomaly_type": "DUPLICATE_ALARM_REPLAY",
            "subtype": "REPLAYED_SOURCE_EVENT",
            "entity_type": "alarm_event",
            "entity_id": dup_ev["id"],
            "machine_id": orig_ev["machine_id"],
            "plant_id": orig_ev["plant_id"],
            "timestamp": orig_ev["event_timestamp"].isoformat(),
            "details": f"Alarm {dup_ev['id']} is an identical replayed duplicate of {orig_ev['id']} (source_event_id: {orig_ev['source_event_id']})."
        })

    alarm_events.extend(replayed_events)
    # Re-sort alarm events chronologically
    alarm_events.sort(key=lambda x: x["event_timestamp"])

    # Scenario E: Corrective action closed without verification
    # Mark action as CLOSED or COMPLETED, but strip verification
    completed_actions = [act for act in corrective_actions if act["status"] in ["COMPLETED", "CLOSED"]]
    num_e = min(config.num_action_closed_unverified, len(completed_actions))
    selected_e = rng.sample(completed_actions, num_e)

    for act in selected_e:
        act["is_verified"] = False
        act["verified_by"] = None
        act["verified_at"] = None
        act["verification_notes"] = None

        gt_id = IdGenerator.anomaly_id(2026, anomaly_counter)
        anomaly_counter += 1
        ground_truth_records.append({
            "anomaly_id": gt_id,
            "anomaly_type": "INCOMPLETE_CORRECTIVE_ACTION",
            "subtype": "CLOSED_WITHOUT_VERIFICATION",
            "entity_type": "corrective_action",
            "entity_id": act["id"],
            "machine_id": None,
            "plant_id": None,
            "timestamp": act["updated_at"].isoformat() if act["updated_at"] else datetime.utcnow().isoformat(),
            "details": f"Action {act['id']} has status '{act['status']}' but is_verified is False and verification timestamp is null."
        })

    summary = {
        "total_anomalies_injected": len(ground_truth_records),
        "ack_before_alarm_count": num_a,
        "impossible_interlock_count": num_b,
        "missing_incident_context_count": num_c,
        "duplicate_alarm_replay_count": num_d,
        "action_closed_unverified_count": num_e,
    }

    return ground_truth_records, summary
