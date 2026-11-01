from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import random
from generator.id_generator import IdGenerator

INCIDENT_PROFILES = [
    ("Critical Hydraulic Line Pressure Surge", "INTERLOCK_FAILURE", "CRITICAL"),
    ("Automated Workcell Safety Enclosure Breach", "SAFETY_BREACH", "CRITICAL"),
    ("Bearing Overheating Runaway & Friction Smoke", "EQUIPMENT_DAMAGE", "HIGH"),
    ("Harmonic Vibration Limit Exceedance with Automated Shutdown", "NEAR_MISS", "MEDIUM"),
    ("Toxic Solvent Vapor Excursion in Reactor Bay", "HAZARDOUS_RELEASE", "CRITICAL"),
    ("Servo Axis Emergency Stop Relay Lockout", "INTERLOCK_FAILURE", "HIGH"),
    ("Conveyor Infeed Jam with Motor Thermal Trip", "NEAR_MISS", "LOW"),
]

INVESTIGATORS = [
    "Dr. Aris Thorne (Chief Safety Officer)",
    "Sarah Jenkins (Senior Reliability Engineer)",
    "Heinrich Mueller (Lead Automation Specialist)",
    "Carlos Ramirez (EHS Incident Investigator)"
]


def generate_incidents_and_actions(
    num_incidents: int,
    alarm_events: List[dict],
    machines: List[dict],
    machine_safety_zones: List[dict],
    shifts: List[dict],
    start_date: datetime,
    end_date: datetime,
    rng: random.Random
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Generate Incidents, IncidentAlarmEvents, and CorrectiveActions with preserved timelines."""
    incidents = []
    incident_alarm_links = []
    corrective_actions = []

    # Map machine to its safety zones
    mch_zones = {}
    for msz in machine_safety_zones:
        mch_zones.setdefault(msz["machine_id"], []).append(msz["safety_zone_id"])

    # High severity alarms that can serve as triggering alarms
    high_sev_alarms = [ev for ev in alarm_events if ev["severity"] in ["CRITICAL", "HIGH"]]
    if not high_sev_alarms:
        high_sev_alarms = alarm_events

    machine_map = {m["id"]: m for m in machines}

    for inc_idx in range(num_incidents):
        inc_seq = inc_idx + 1
        inc_id = IdGenerator.incident_id(2026, inc_seq)

        # Select a triggering alarm
        trigger_alm = high_sev_alarms[inc_idx % len(high_sev_alarms)]
        alm_time = trigger_alm["event_timestamp"]
        m_id = trigger_alm["machine_id"]
        p_id = trigger_alm["plant_id"]

        # Incident occurs shortly after alarm trigger
        inc_created = alm_time + timedelta(minutes=rng.randint(2, 20))
        if inc_created >= end_date:
            inc_created = end_date - timedelta(hours=2)

        prof_title, prof_type, prof_sev = INCIDENT_PROFILES[inc_idx % len(INCIDENT_PROFILES)]
        zones = mch_zones.get(m_id, [None])
        sz_id = zones[0] if zones else None

        # Timeline progression
        # Status distribution: 60% CLOSED, 25% RESOLVED, 10% CONTAINED, 5% OPEN
        status_choice = rng.choices(
            ["CLOSED", "RESOLVED", "CONTAINED", "OPEN"],
            weights=[0.60, 0.25, 0.10, 0.05]
        )[0]

        contained_time = None
        resolved_time = None
        closed_time = None

        if status_choice in ["CONTAINED", "RESOLVED", "CLOSED"]:
            contained_time = inc_created + timedelta(hours=rng.randint(1, 4))
        if status_choice in ["RESOLVED", "CLOSED"]:
            resolved_time = contained_time + timedelta(hours=rng.randint(6, 24))
        if status_choice == "CLOSED":
            closed_time = resolved_time + timedelta(hours=rng.randint(2, 12))

        # Assign investigator
        investigator = rng.choice(INVESTIGATORS)

        incidents.append({
            "id": inc_id,
            "plant_id": p_id,
            "machine_id": m_id,
            "safety_zone_id": sz_id,
            "triggering_alarm_id": trigger_alm["id"],
            "title": f"{machine_map.get(m_id, {}).get('name', m_id)}: {prof_title}",
            "description": f"Incident triggered following alarm {trigger_alm['id']}. Root cause analysis initiated under standard industrial safety guidelines.",
            "incident_type": prof_type,
            "severity": prof_sev,
            "status": status_choice,
            "assigned_investigator": investigator,
            "operator_shift_id": None,
            "created_timestamp": inc_created,
            "contained_timestamp": contained_time,
            "resolved_timestamp": resolved_time,
            "closed_timestamp": closed_time,
        })

        # Link triggering alarm in bridge table
        incident_alarm_links.append({
            "incident_id": inc_id,
            "alarm_event_id": trigger_alm["id"],
            "relationship_type": "TRIGGER",
            "created_at": inc_created,
        })

        # Generate 1 to 2 corrective actions per incident
        num_actions = rng.choice([1, 2])
        for act_i in range(num_actions):
            act_id = IdGenerator.corrective_action_id(inc_id, act_i + 1)
            due_date = inc_created + timedelta(days=rng.randint(3, 14))

            if status_choice == "CLOSED":
                act_status = "CLOSED"
                completed_at = inc_created + timedelta(hours=rng.randint(4, 20))
                # For valid baseline, closed action MUST be verified
                is_verified = True
                verified_by = investigator
                verified_at = completed_at + timedelta(hours=rng.randint(1, 6))
                v_notes = "Physical safety verification completed and verified operational tolerances."
            elif status_choice == "RESOLVED":
                act_status = "COMPLETED"
                completed_at = inc_created + timedelta(hours=rng.randint(4, 20))
                is_verified = True
                verified_by = investigator
                verified_at = completed_at + timedelta(hours=rng.randint(1, 6))
                v_notes = "Remedial procedure complete and pre-run interlock checks passed."
            elif status_choice == "CONTAINED":
                act_status = "IN_PROGRESS"
                completed_at = None
                is_verified = False
                verified_by = None
                verified_at = None
                v_notes = None
            else:
                act_status = "PENDING"
                completed_at = None
                is_verified = False
                verified_by = None
                verified_at = None
                v_notes = None

            action_titles = [
                "Recalibrate optical light curtain alignment and trip relay",
                "Replace degraded hydraulic seal pack and pressure relief diaphragm",
                "Update PLC firmware safety interlocking threshold parameters",
                "Execute mandatory Lockout/Tagout refresher for shift operators",
            ]

            corrective_actions.append({
                "id": act_id,
                "incident_id": inc_id,
                "title": action_titles[(inc_idx + act_i) % len(action_titles)],
                "description": f"Mandatory remediation stemming from safety incident {inc_id}.",
                "assigned_to": rng.choice(["Devon Brooks", "Kenji Sato", "Liam O'Connor", "Elena Rostova"]),
                "priority": prof_sev,
                "due_date": due_date,
                "completed_at": completed_at,
                "status": act_status,
                "verification_required": True,
                "is_verified": is_verified,
                "verified_by": verified_by,
                "verified_at": verified_at,
                "verification_notes": v_notes,
                "created_at": inc_created,
                "updated_at": verified_at or completed_at or inc_created,
            })

    incidents.sort(key=lambda x: x["created_timestamp"])
    return incidents, incident_alarm_links, corrective_actions
