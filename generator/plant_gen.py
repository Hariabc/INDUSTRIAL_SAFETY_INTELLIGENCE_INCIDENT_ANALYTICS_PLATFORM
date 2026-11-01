from datetime import datetime
from typing import List, Tuple
import random
from generator.id_generator import IdGenerator

PLANT_PROFILES = [
    {
        "name": "Apex Advanced Propulsion Facility",
        "location": "Detroit, Michigan, USA",
        "total_lines": 6,
        "base_safety_score": 94.5,
    },
    {
        "name": "Bavaria Precision Robotics & Pressworks",
        "location": "Munich, Germany",
        "total_lines": 8,
        "base_safety_score": 97.2,
    },
    {
        "name": "Shenzhen Autonomous Assembly Gigafactory",
        "location": "Shenzhen, Guangdong, China",
        "total_lines": 12,
        "base_safety_score": 91.8,
    },
    {
        "name": "Solway Chemical Synthesis & Cryogenics",
        "location": "Billingham, Teesside, UK",
        "total_lines": 5,
        "base_safety_score": 89.4,
    },
]

ZONE_TYPES = ["HAZARDOUS", "EXCLUSION", "CONTROLLED", "GENERAL"]
HAZARD_LEVELS = ["HIGH", "MEDIUM", "LOW"]


def generate_plants(num_plants: int, start_date: datetime) -> Tuple[List[dict], List[dict]]:
    """Generate Plant and SafetyZone records deterministically."""
    plants = []
    safety_zones = []

    for i in range(num_plants):
        plant_id = IdGenerator.plant_id(i + 1)
        profile = PLANT_PROFILES[i % len(PLANT_PROFILES)]
        plant_record = {
            "id": plant_id,
            "name": profile["name"],
            "location": profile["location"],
            "operational_status": "ACTIVE",
            "total_lines": profile["total_lines"],
            "safety_score": profile["base_safety_score"],
            "created_at": start_date,
            "updated_at": start_date,
        }
        plants.append(plant_record)

        # Generate 4-6 safety zones per plant
        zones_count = 5
        zone_specs = [
            ("Primary Robotic Enclosure", "EXCLUSION", "HIGH", 0),
            ("High Pressure Hydraulic Bay", "HAZARDOUS", "HIGH", 3),
            ("Thermal Annealing & Furnace Area", "HAZARDOUS", "MEDIUM", 4),
            ("Automated Conveyance Corridor", "CONTROLLED", "MEDIUM", 8),
            ("Operator Supervision & QC Deck", "GENERAL", "LOW", 20),
        ]

        for z_idx, (z_name, z_type, z_hazard, z_occ) in enumerate(zone_specs, 1):
            zone_id = IdGenerator.safety_zone_id(plant_id, z_idx)
            safety_zones.append({
                "id": zone_id,
                "plant_id": plant_id,
                "name": f"{profile['name'].split()[0]} {z_name}",
                "zone_type": z_type,
                "hazard_level": z_hazard,
                "max_occupancy": z_occ,
                "created_at": start_date,
            })

    return plants, safety_zones
