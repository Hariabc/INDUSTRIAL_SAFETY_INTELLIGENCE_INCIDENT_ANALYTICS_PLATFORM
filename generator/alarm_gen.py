from datetime import datetime, timedelta
from typing import List, Tuple, Dict
import random
from generator.id_generator import IdGenerator

ALARM_CATEGORIES = [
    ("SAFETY_INTERLOCK", "Critical Safety Interlock Trip or Open Circuit", "CRITICAL", 300, 0.12),
    ("OVERHEATING", "Bearing / Winding Temperature Exceedance", "HIGH", 900, 0.18),
    ("PRESSURE_ANOMALY", "Hydraulic Line Pressure Out of Range", "HIGH", 900, 0.15),
    ("VIBRATION", "Radial Shaft Harmonic Vibration Warning", "MEDIUM", 1800, 0.20),
    ("EMERGENCY_SHUTDOWN", "Operator E-Stop Trigger Activated", "CRITICAL", 300, 0.08),
    ("TOXIC_GAS", "Atmospheric VOC / Toxic Gas Concentration Alert", "CRITICAL", 300, 0.07),
    ("ELECTRICAL_FAULT", "Ground Fault / Phase Imbalance Detected", "MEDIUM", 1800, 0.12),
    ("PROCESS_DEVIATION", "Conveyor Feed Speed Mismatch", "LOW", 3600, 0.08),
]

ENGINEERING_UNITS = {
    "OVERHEATING": ("°C", 45.0, 110.0, 85.0),
    "PRESSURE_ANOMALY": ("bar", 10.0, 350.0, 240.0),
    "VIBRATION": ("mm/s", 0.5, 18.0, 7.5),
    "TOXIC_GAS": ("ppm", 0.0, 50.0, 15.0),
    "PROCESS_DEVIATION": ("rpm", 100.0, 3600.0, 2800.0),
}


def generate_alarm_definitions(num_definitions: int, start_date: datetime) -> List[dict]:
    """Generate 200 AlarmDefinition catalog entries."""
    definitions = []

    for i in range(num_definitions):
        def_id = IdGenerator.alarm_definition_id(i + 1)
        cat_info = ALARM_CATEGORIES[i % len(ALARM_CATEGORIES)]
        cat_name, cat_desc, severity, sla_secs, _ = cat_info

        code = f"ALM-CODE-{i + 1:04d}"
        name = f"{cat_name.replace('_', ' ').title()} - Class {((i // len(ALARM_CATEGORIES)) % 10) + 1}"

        definitions.append({
            "id": def_id,
            "code": code,
            "name": name,
            "description": f"{cat_desc} (Specification Ref: ISO-13849/IEC-62061 standard check #{i + 1}).",
            "severity": severity,
            "category": cat_name,
            "ack_sla_seconds": sla_secs,
            "requires_clearance": True if severity in ["CRITICAL", "HIGH"] else False,
            "created_at": start_date - timedelta(days=60),
        })

    return definitions


def generate_alarm_events_and_acknowledgements(
    num_events: int,
    definitions: List[dict],
    machines: List[dict],
    shifts: List[dict],
    start_date: datetime,
    end_date: datetime,
    rng: random.Random
) -> Tuple[List[dict], List[dict]]:
    """Generate 50,000 alarm events and corresponding acknowledgements."""
    alarm_events = []
    acknowledgements = []

    # Map shifts by plant
    shifts_by_plant = {}
    for s in shifts:
        shifts_by_plant.setdefault(s["plant_id"], []).append(s)

    # Machine sequence counters for deterministic IDs: ALM-<machine-id>-000001
    machine_seq: Dict[str, int] = {m["id"]: 0 for m in machines}
    machine_by_id = {m["id"]: m for m in machines}

    total_duration_secs = int((end_date - start_date).total_seconds())

    # Pre-select machines for specific patterns:
    # 5 machines will experience repeated unsafe alarms
    repeated_unsafe_machines = [machines[i]["id"] for i in [2, 7, 14, 25, 42]]
    # 3 definitions will act as high-frequency nuisance alarms
    nuisance_defs = [definitions[d] for d in [3, 11, 23]]
    for nd in nuisance_defs:
        nd["severity"] = "LOW"

    # Plan event distribution:
    # ~70% standard background alarms
    # ~15% alarm floods (bursts of 15-30 events within 10 min window)
    # ~10% nuisance/chattering alarms
    # ~5% high-severity repeated unsafe clusters
    num_floods = 30
    events_in_floods = num_floods * 25
    num_nuisance_events = int(num_events * 0.12)
    num_repeated_unsafe = int(num_events * 0.06)
    standard_events = num_events - events_in_floods - num_nuisance_events - num_repeated_unsafe

    # 1. Standard events
    for _ in range(standard_events):
        m = rng.choice(machines)
        m_id = m["id"]
        p_id = m["plant_id"]
        d = rng.choice(definitions)

        offset_secs = rng.randint(0, total_duration_secs)
        evt_time = start_date + timedelta(seconds=offset_secs)
        machine_seq[m_id] += 1
        evt_id = IdGenerator.alarm_event_id(m_id, machine_seq[m_id])
        src_id = f"SRC-EVT-{m_id}-{machine_seq[m_id]:06d}"

        val_info = ENGINEERING_UNITS.get(d["category"], (None, None, None, None))
        val = round(rng.uniform(val_info[1], val_info[2]), 2) if val_info[0] else None

        alarm_events.append({
            "id": evt_id,
            "alarm_definition_id": d["id"],
            "machine_id": m_id,
            "plant_id": p_id,
            "severity": d["severity"],
            "source_event_id": src_id,
            "value": val,
            "threshold": val_info[3] if val_info[0] else None,
            "unit": val_info[0],
            "status": "ACKNOWLEDGED",
            "event_timestamp": evt_time,
            "cleared_timestamp": evt_time + timedelta(minutes=rng.randint(5, 120)),
            "is_nuisance": False,
            "created_at": evt_time,
        })

    # 2. Alarm floods (bursts)
    for f_idx in range(num_floods):
        flood_machine = rng.choice(machines)
        fm_id = flood_machine["id"]
        fp_id = flood_machine["plant_id"]
        flood_start_offset = rng.randint(0, total_duration_secs - 3600)
        flood_start_time = start_date + timedelta(seconds=flood_start_offset)

        for burst_i in range(25):
            d = rng.choice(definitions)
            burst_time = flood_start_time + timedelta(seconds=burst_i * 20 + rng.randint(1, 10))
            machine_seq[fm_id] += 1
            evt_id = IdGenerator.alarm_event_id(fm_id, machine_seq[fm_id])
            src_id = f"SRC-EVT-{fm_id}-{machine_seq[fm_id]:06d}"

            alarm_events.append({
                "id": evt_id,
                "alarm_definition_id": d["id"],
                "machine_id": fm_id,
                "plant_id": fp_id,
                "severity": d["severity"],
                "source_event_id": src_id,
                "value": round(rng.uniform(70.0, 95.0), 2),
                "threshold": 75.0,
                "unit": "°C",
                "status": "ACKNOWLEDGED",
                "event_timestamp": burst_time,
                "cleared_timestamp": burst_time + timedelta(minutes=rng.randint(10, 60)),
                "is_nuisance": False,
                "created_at": burst_time,
            })

    # 3. Nuisance / Chattering Alarms
    for _ in range(num_nuisance_events):
        m = rng.choice(machines)
        m_id = m["id"]
        p_id = m["plant_id"]
        d = rng.choice(nuisance_defs)

        offset_secs = rng.randint(0, total_duration_secs)
        evt_time = start_date + timedelta(seconds=offset_secs)
        machine_seq[m_id] += 1
        evt_id = IdGenerator.alarm_event_id(m_id, machine_seq[m_id])
        src_id = f"SRC-EVT-{m_id}-{machine_seq[m_id]:06d}"

        alarm_events.append({
            "id": evt_id,
            "alarm_definition_id": d["id"],
            "machine_id": m_id,
            "plant_id": p_id,
            "severity": "LOW",
            "source_event_id": src_id,
            "value": round(rng.uniform(1.0, 3.0), 2),
            "threshold": 2.5,
            "unit": "mm/s",
            "status": "ACKNOWLEDGED",
            "event_timestamp": evt_time,
            "cleared_timestamp": evt_time + timedelta(minutes=rng.randint(1, 10)),
            "is_nuisance": True,
            "created_at": evt_time,
        })

    # 4. Repeated Unsafe Condition clusters
    for _ in range(num_repeated_unsafe):
        m_id = rng.choice(repeated_unsafe_machines)
        m = machine_by_id[m_id]
        p_id = m["plant_id"]
        # Select high severity definition
        crit_defs = [d for d in definitions if d["severity"] in ["CRITICAL", "HIGH"]]
        d = rng.choice(crit_defs)

        offset_secs = rng.randint(0, total_duration_secs)
        evt_time = start_date + timedelta(seconds=offset_secs)
        machine_seq[m_id] += 1
        evt_id = IdGenerator.alarm_event_id(m_id, machine_seq[m_id])
        src_id = f"SRC-EVT-{m_id}-{machine_seq[m_id]:06d}"

        alarm_events.append({
            "id": evt_id,
            "alarm_definition_id": d["id"],
            "machine_id": m_id,
            "plant_id": p_id,
            "severity": d["severity"],
            "source_event_id": src_id,
            "value": round(rng.uniform(90.0, 140.0), 2),
            "threshold": 85.0,
            "unit": "°C",
            "status": "ACKNOWLEDGED",
            "event_timestamp": evt_time,
            "cleared_timestamp": evt_time + timedelta(minutes=rng.randint(15, 180)),
            "is_nuisance": False,
            "created_at": evt_time,
        })

    # Sort strictly chronologically
    alarm_events.sort(key=lambda x: x["event_timestamp"])

    # Lookup def SLA
    def_sla_map = {d["id"]: d["ack_sla_seconds"] for d in definitions}

    # Generate acknowledgements for baseline alarm events
    ack_seq = 1
    for ev in alarm_events:
        evt_time = ev["event_timestamp"]
        sla_seconds = def_sla_map.get(ev["alarm_definition_id"], 1800)

        # 85% within SLA, 15% delayed
        if rng.random() < 0.85:
            delay_secs = rng.uniform(30.0, max(45.0, sla_seconds * 0.75))
            sla_status = "WITHIN_SLA"
        else:
            delay_secs = rng.uniform(sla_seconds * 1.05, sla_seconds * 2.5)
            sla_status = "DELAYED"

        ack_time = evt_time + timedelta(seconds=delay_secs)
        ack_id = IdGenerator.acknowledgement_id(ev["id"], 1)

        # Find plant shift
        plant_shifts = shifts_by_plant.get(ev["plant_id"], [])
        shift_id = None
        for s in plant_shifts:
            if s["shift_start"] <= ack_time <= s["shift_end"]:
                shift_id = s["id"]
                break

        lead_op = rng.choice(["Marcus Vance", "Elena Rostova", "Devon Brooks", "Kenji Sato", "Fatima Al-Mansoor"])

        acknowledgements.append({
            "id": ack_id,
            "alarm_event_id": ev["id"],
            "operator_name": lead_op,
            "operator_shift_id": shift_id,
            "ack_timestamp": ack_time,
            "ack_delay_seconds": round(delay_secs, 2),
            "sla_status": sla_status,
            "notes": "Verified telemetry and initiated field diagnostics." if sla_status == "DELAYED" else "Standard acknowledge.",
            "created_at": ack_time,
        })
        ack_seq += 1

    return alarm_events, acknowledgements
