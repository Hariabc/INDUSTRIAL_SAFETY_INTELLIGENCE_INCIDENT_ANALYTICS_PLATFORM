from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.app.database import get_db
from backend.app.models import Plant, Machine, SafetyZone, AlarmEvent, Incident
from backend.app.schemas.plant import PlantDetailSchema

router = APIRouter(prefix="/plants", tags=["Plants"])


@router.get("", response_model=List[PlantDetailSchema])
def list_plants(db: Session = Depends(get_db)):
    """List all plants with aggregate machine counts and active safety metrics."""
    plants = db.query(Plant).all()
    results = []

    for p in plants:
        m_count = db.query(Machine).filter(Machine.plant_id == p.id).count()
        act_alarms = db.query(AlarmEvent).filter(
            AlarmEvent.plant_id == p.id,
            AlarmEvent.status == "ACTIVE"
        ).count()
        crit_incidents = db.query(Incident).filter(
            Incident.plant_id == p.id,
            Incident.severity == "CRITICAL",
            Incident.status.in_(["OPEN", "INVESTIGATING", "CONTAINED"])
        ).count()

        zones = db.query(SafetyZone).filter(SafetyZone.plant_id == p.id).all()

        results.append({
            "id": p.id,
            "name": p.name,
            "location": p.location,
            "operational_status": p.operational_status,
            "total_lines": p.total_lines,
            "safety_score": p.safety_score,
            "created_at": p.created_at,
            "updated_at": p.updated_at,
            "machines_count": m_count,
            "active_alarms_count": act_alarms,
            "critical_incidents_count": crit_incidents,
            "safety_zones": zones,
        })

    return results


@router.get("/{plant_id}")
def get_plant_detail(plant_id: str, db: Session = Depends(get_db)):
    """Get plant details along with its machines and safety zones."""
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Plant not found")

    machines = db.query(Machine).filter(Machine.plant_id == plant_id).all()
    safety_zones = db.query(SafetyZone).filter(SafetyZone.plant_id == plant_id).all()

    total_alarms = db.query(AlarmEvent).filter(AlarmEvent.plant_id == plant_id).count()
    critical_alarms = db.query(AlarmEvent).filter(
        AlarmEvent.plant_id == plant_id,
        AlarmEvent.severity == "CRITICAL"
    ).count()
    incidents_count = db.query(Incident).filter(Incident.plant_id == plant_id).count()

    return {
        "plant": {
            "id": plant.id,
            "name": plant.name,
            "location": plant.location,
            "operational_status": plant.operational_status,
            "total_lines": plant.total_lines,
            "safety_score": plant.safety_score,
            "created_at": plant.created_at.isoformat(),
            "updated_at": plant.updated_at.isoformat(),
        },
        "stats": {
            "machine_count": len(machines),
            "safety_zone_count": len(safety_zones),
            "total_alarms": total_alarms,
            "critical_alarms": critical_alarms,
            "incidents_count": incidents_count,
        },
        "safety_zones": [
            {
                "id": z.id,
                "name": z.name,
                "zone_type": z.zone_type,
                "hazard_level": z.hazard_level,
                "max_occupancy": z.max_occupancy,
            }
            for z in safety_zones
        ],
        "machines": [
            {
                "id": m.id,
                "name": m.name,
                "type": m.type,
                "model_number": m.model_number,
                "current_state": m.current_state,
                "criticality": m.criticality,
                "is_isolated": m.is_isolated,
            }
            for m in machines
        ]
    }
