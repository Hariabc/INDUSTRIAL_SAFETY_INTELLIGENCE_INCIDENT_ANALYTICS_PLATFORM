from datetime import datetime, timedelta
from typing import List, Tuple
import random
from generator.id_generator import IdGenerator

OPERATORS = [
    "Marcus Vance", "Elena Rostova", "Devon Brooks", "Kenji Sato",
    "Fatima Al-Mansoor", "Lukas Weber", "Chloe Dubois", "Rajesh Nair",
    "Sofia Rossi", "Liam O'Connor", "Astrid Lindholm", "Mateo Hernandez"
]

MACHINE_STATES = ["RUNNING", "IDLE", "TRIPPED", "EMERGENCY_STOP", "MAINTENANCE", "UNSAFE"]


def generate_operator_shifts(
    plants: List[dict],
    start_date: datetime,
    simulation_days: int,
    rng: random.Random
) -> List[dict]:
    """Generate 3 daily 8-hour shifts for each plant across simulation days."""
    shifts = []
    shift_seq = 1

    shift_names = [
        ("MORNING", 6, 14),
        ("AFTERNOON", 14, 22),
        ("NIGHT", 22, 6)  # crosses midnight
    ]

    for day in range(simulation_days):
        day_date = start_date + timedelta(days=day)

        for plant in plants:
            plant_id = plant["id"]

            for s_name, start_hr, end_hr in shift_names:
                shift_id = IdGenerator.operator_shift_id(shift_seq)
                shift_seq += 1

                shift_start = day_date.replace(hour=start_hr, minute=0, second=0)
                if end_hr < start_hr:
                    shift_end = (day_date + timedelta(days=1)).replace(hour=end_hr, minute=0, second=0)
                else:
                    shift_end = day_date.replace(hour=end_hr, minute=0, second=0)

                lead_op = OPERATORS[(shift_seq + day) % len(OPERATORS)]

                shifts.append({
                    "id": shift_id,
                    "plant_id": plant_id,
                    "shift_name": s_name,
                    "lead_operator_name": lead_op,
                    "shift_start": shift_start,
                    "shift_end": shift_end,
                    "created_at": shift_start - timedelta(days=1),
                })

    return shifts


def generate_machine_state_events(
    machines: List[dict],
    shifts: List[dict],
    start_date: datetime,
    end_date: datetime,
    rng: random.Random
) -> List[dict]:
    """Generate chronological machine state transitions over the simulation window."""
    state_events = []

    # Map shifts by plant and start time for fast lookup
    shifts_by_plant = {}
    for s in shifts:
        shifts_by_plant.setdefault(s["plant_id"], []).append(s)

    for m in machines:
        m_id = m["id"]
        p_id = m["plant_id"]
        plant_shifts = shifts_by_plant.get(p_id, [])

        curr_time = start_date + timedelta(hours=rng.randint(0, 12))
        curr_state = "RUNNING"

        # Record initial baseline state
        state_events.append({
            "machine_id": m_id,
            "plant_id": p_id,
            "previous_state": None,
            "new_state": curr_state,
            "reason": "Normal production startup cycle",
            "operator_shift_id": plant_shifts[0]["id"] if plant_shifts else None,
            "timestamp": curr_time,
        })

        # Average 15-30 state changes per machine over 30 days
        num_transitions = rng.randint(15, 30)

        for _ in range(num_transitions):
            delta_hours = rng.uniform(8, 48)
            curr_time += timedelta(hours=delta_hours)
            if curr_time >= end_date:
                break

            prev_state = curr_state

            # State transition probabilities
            if prev_state == "RUNNING":
                curr_state = rng.choices(
                    ["IDLE", "MAINTENANCE", "TRIPPED", "UNSAFE"],
                    weights=[0.60, 0.25, 0.10, 0.05]
                )[0]
                reason = {
                    "IDLE": "Production batch changeover",
                    "MAINTENANCE": "Scheduled preventive lubrication",
                    "TRIPPED": "Excessive bearing vibration detected",
                    "UNSAFE": "Safety perimeter breach signal"
                }[curr_state]
            elif prev_state == "IDLE":
                curr_state = "RUNNING" if rng.random() > 0.15 else "MAINTENANCE"
                reason = "Resuming scheduled manufacturing run" if curr_state == "RUNNING" else "Pre-flight calibration"
            elif prev_state == "TRIPPED":
                curr_state = "MAINTENANCE" if rng.random() > 0.4 else "IDLE"
                reason = "Reset after trip clearance"
            elif prev_state == "UNSAFE":
                curr_state = "EMERGENCY_STOP" if rng.random() > 0.5 else "MAINTENANCE"
                reason = "Interlock failsafe engagement"
            elif prev_state == "EMERGENCY_STOP":
                curr_state = "MAINTENANCE"
                reason = "Post-E-stop diagnostics and containment"
            elif prev_state == "MAINTENANCE":
                curr_state = "IDLE" if rng.random() > 0.3 else "RUNNING"
                reason = "Maintenance work order completed and signed off"

            # Locate shift on duty at curr_time
            matching_shift = None
            for s in plant_shifts:
                if s["shift_start"] <= curr_time <= s["shift_end"]:
                    matching_shift = s["id"]
                    break

            state_events.append({
                "machine_id": m_id,
                "plant_id": p_id,
                "previous_state": prev_state,
                "new_state": curr_state,
                "reason": reason,
                "operator_shift_id": matching_shift,
                "timestamp": curr_time,
            })

    # Sort strictly chronologically
    state_events.sort(key=lambda x: x["timestamp"])
    return state_events
