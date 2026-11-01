from datetime import datetime, timedelta
from typing import List, Tuple
import random
from generator.id_generator import IdGenerator

MACHINE_TYPES = [
    ("ROBOTIC_ARM", "KUKA KR-Quantic High-Payload Articulated Arm"),
    ("HYDRAULIC_PRESS", "Schuler 2000-Ton Servo Forging Press"),
    ("TURBINE", "Siemens SGT-400 High Pressure Gas Turbine"),
    ("CONVEYOR", "FlexLink Heavy Industrial Roller Feed"),
    ("COMPRESSOR", "Atlas Copco Oil-Free Rotary Screw Air Compressor"),
    ("REACTOR", "Pfaudler Glass-Lined Catalytic Hydro-Reactor"),
    ("CNC_MILL", "DMG MORI 5-Axis Precision Machining Center"),
]

INTERLOCK_TEMPLATES = [
    ("Optical Light Curtain Barrier", "LIGHT_CURTAIN", True, False),
    ("Dual-Channel Emergency Stop Relay", "E_STOP_CIRCUIT", True, False),
    ("Mechanical Door Safety Interlock", "HARDWARE_GUARD", True, True),
    ("Thermal Over-Limit Cutoff Sensor", "THERMAL_CUTOFF", True, False),
    ("Proportional Pressure Relief Valve", "PRESSURE_RELIEF", True, False),
]


def generate_machines(
    num_machines: int,
    plants: List[dict],
    safety_zones: List[dict],
    start_date: datetime,
    rng: random.Random
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Generate Machine, MachineSafetyZone, and Interlock records."""
    machines = []
    machine_safety_zones = []
    interlocks = []

    # Map zones by plant_id for fast lookup
    plant_zones = {}
    for z in safety_zones:
        plant_zones.setdefault(z["plant_id"], []).append(z)

    machines_per_plant = num_machines // len(plants)

    for i in range(num_machines):
        m_id = IdGenerator.machine_id(i + 1)
        plant_idx = min(i // machines_per_plant, len(plants) - 1)
        plant = plants[plant_idx]
        plant_id = plant["id"]

        m_type, m_model = MACHINE_TYPES[i % len(MACHINE_TYPES)]
        commission_date = start_date - timedelta(days=rng.randint(180, 1500))

        # Assign criticality
        if i % 5 == 0:
            criticality = "CRITICAL"
        elif i % 3 == 0:
            criticality = "HIGH"
        elif i % 2 == 0:
            criticality = "MEDIUM"
        else:
            criticality = "LOW"

        initial_state = "RUNNING" if rng.random() > 0.15 else rng.choice(["IDLE", "MAINTENANCE"])

        machine_record = {
            "id": m_id,
            "plant_id": plant_id,
            "name": f"{plant['name'].split()[0]} {m_type.replace('_', ' ').title()} #{i + 1}",
            "type": m_type,
            "model_number": m_model,
            "installation_date": commission_date,
            "current_state": initial_state,
            "criticality": criticality,
            "is_isolated": False,
            "created_at": commission_date,
            "updated_at": start_date,
        }
        machines.append(machine_record)

        # Assign machine to safety zones (Primary + optional Secondary)
        available_zones = plant_zones.get(plant_id, [])
        if available_zones:
            primary_zone = available_zones[i % len(available_zones)]
            machine_safety_zones.append({
                "machine_id": m_id,
                "safety_zone_id": primary_zone["id"],
                "coverage_type": "PRIMARY",
                "created_at": commission_date,
            })
            if rng.random() > 0.6 and len(available_zones) > 1:
                secondary_zone = available_zones[(i + 1) % len(available_zones)]
                machine_safety_zones.append({
                    "machine_id": m_id,
                    "safety_zone_id": secondary_zone["id"],
                    "coverage_type": "SECONDARY",
                    "created_at": commission_date,
                })

        # Generate 3-4 interlocks per machine
        num_itls = rng.choice([3, 4])
        for itl_idx in range(num_itls):
            tmpl = INTERLOCK_TEMPLATES[itl_idx % len(INTERLOCK_TEMPLATES)]
            itl_id = IdGenerator.interlock_id(m_id, itl_idx + 1)
            interlocks.append({
                "id": itl_id,
                "machine_id": m_id,
                "name": f"{tmpl[0]} - Unit {itl_idx + 1}",
                "interlock_type": tmpl[1],
                "target_state": "ENGAGED",
                "current_state": "ENGAGED",
                "is_safety_critical": tmpl[2],
                "bypass_allowed": tmpl[3],
                "last_tested_at": start_date - timedelta(days=rng.randint(1, 30)),
                "created_at": commission_date,
                "updated_at": start_date,
            })

    return machines, machine_safety_zones, interlocks
