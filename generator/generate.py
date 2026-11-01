import argparse
import time
import random
import sys
import os
from datetime import datetime

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from generator.config import GeneratorConfig
from generator.plant_gen import generate_plants
from generator.machine_gen import generate_machines
from generator.alarm_gen import (
    generate_alarm_definitions,
    generate_alarm_events_and_acknowledgements,
)
from generator.state_gen import generate_operator_shifts, generate_machine_state_events
from generator.incident_gen import generate_incidents_and_actions
from generator.anomaly_injector import inject_anomalies
from generator.exporter import DataExporter


def run_pipeline(config: GeneratorConfig, load_db: bool = False):
    """Execute complete deterministic synthetic data generation pipeline."""
    print(f"================================================================")
    print(f"  INDUSTRIAL SAFETY INTELLIGENCE PLATFORM - DATA ENGINE")
    print(f"  Seed: {config.seed} | Simulation Days: {config.simulation_days} | Target Alarms: {config.num_alarm_events}")
    print(f"================================================================")

    start_time = time.time()
    rng = random.Random(config.seed)

    # Step 1 & 3: Plants & Safety Zones
    print("\n[Step 1 & 3] Generating Plants and Safety Zones...")
    plants, safety_zones = generate_plants(config.num_plants, config.start_date)
    print(f"  -> Generated {len(plants)} Plants, {len(safety_zones)} Safety Zones")

    # Step 2, 4, 5: Machines, MachineSafetyZones, Interlocks
    print("\n[Step 2, 4, 5] Generating Machines, Zone Associations, and Interlocks...")
    machines, machine_safety_zones, interlocks = generate_machines(
        config.num_machines, plants, safety_zones, config.start_date, rng
    )
    print(f"  -> Generated {len(machines)} Machines, {len(machine_safety_zones)} MachineSafetyZones, {len(interlocks)} Interlocks")

    # Step 6: Alarm Definitions
    print("\n[Step 6] Generating Alarm Definitions Catalog...")
    alarm_definitions = generate_alarm_definitions(config.num_alarm_definitions, config.start_date)
    print(f"  -> Generated {len(alarm_definitions)} Alarm Definitions with SLAs")

    # Step 7: Operator Shifts
    print("\n[Step 7] Generating Operator Shifts (8-hour rotating schedules)...")
    shifts = generate_operator_shifts(plants, config.start_date, config.simulation_days, rng)
    print(f"  -> Generated {len(shifts)} Operator Shifts across {config.simulation_days} days")

    # Step 8: Machine State Transitions
    print("\n[Step 8] Generating Machine State Event Histories (append-only)...")
    machine_state_events = generate_machine_state_events(
        machines, shifts, config.start_date, config.end_date, rng
    )
    print(f"  -> Generated {len(machine_state_events)} Machine State Transitions")

    # Step 9 & 10: Alarm Events and Acknowledgements
    print("\n[Step 9 & 10] Generating Baseline Alarm Events and Acknowledgements...")
    alarm_events, acknowledgements = generate_alarm_events_and_acknowledgements(
        config.num_alarm_events, alarm_definitions, machines, shifts,
        config.start_date, config.end_date, rng
    )
    print(f"  -> Generated {len(alarm_events)} Alarm Events, {len(acknowledgements)} Acknowledgements")

    # Step 11 & 12: Incidents, IncidentAlarmEvents, CorrectiveActions
    print("\n[Step 11 & 12] Generating Incidents and Corrective Actions...")
    # Generate around 120 incidents
    num_incidents = 120
    incidents, incident_alarm_links, corrective_actions = generate_incidents_and_actions(
        num_incidents, alarm_events, machines, machine_safety_zones, shifts,
        config.start_date, config.end_date, rng
    )
    print(f"  -> Generated {len(incidents)} Incidents, {len(incident_alarm_links)} IncidentAlarmLinks, {len(corrective_actions)} Corrective Actions")

    # Deliberate Anomaly Injection (Ground Truth separation)
    print("\n[Anomaly Injection] Injecting 5 Deliberate Anomaly Scenarios...")
    ground_truth, injection_summary = inject_anomalies(
        alarm_events, acknowledgements, machines, interlocks, incidents,
        corrective_actions, config, rng
    )
    print(f"  -> Injected {injection_summary['total_anomalies_injected']} anomalies across 5 scenarios:")
    print(f"     - Acknowledgement Before Alarm: {injection_summary['ack_before_alarm_count']}")
    print(f"     - Impossible Interlock State:   {injection_summary['impossible_interlock_count']}")
    print(f"     - Missing Incident Context:     {injection_summary['missing_incident_context_count']}")
    print(f"     - Duplicate Alarm Replay:       {injection_summary['duplicate_alarm_replay_count']}")
    print(f"     - Unverified Action Closed:     {injection_summary['action_closed_unverified_count']}")

    # Export datasets
    print("\n[Export] Writing CSV, JSON, SQL seed, and ground truth files...")
    datasets = {
        "plants": plants,
        "safety_zones": safety_zones,
        "machines": machines,
        "machine_safety_zones": machine_safety_zones,
        "interlocks": interlocks,
        "alarm_definitions": alarm_definitions,
        "operator_shifts": shifts,
        "machine_state_events": machine_state_events,
        "alarm_events": alarm_events,
        "acknowledgements": acknowledgements,
        "incidents": incidents,
        "incident_alarm_events": incident_alarm_links,
        "corrective_actions": corrective_actions,
    }

    elapsed = time.time() - start_time
    exporter = DataExporter(output_dir="data")
    manifest = exporter.export_all(datasets, ground_truth, config, elapsed)

    print(f"  -> Manifest created with SHA256 checksums at data/source_manifest.json")
    print(f"  -> Ground truth saved to data/ground_truth.csv and data/ground_truth.json")

    # Optional database load
    if load_db:
        print("\n[Database] Loading datasets into database...")
        load_into_database(datasets)
        print("  -> Database ingestion completed.")

    print(f"\n================================================================")
    print(f"  GENERATION COMPLETE in {elapsed:.2f}s")
    print(f"================================================================")
    return datasets, ground_truth, manifest


def load_into_database(datasets: dict):
    """Load generated dataset dictionaries directly into the database."""
    from backend.app.database import SessionLocal, engine, Base
    from backend.app.models import (
        Plant, SafetyZone, MachineSafetyZone, Machine, Interlock,
        OperatorShift, MachineStateEvent, AlarmDefinition, AlarmEvent,
        Acknowledgement, Incident, IncidentAlarmEvent, CorrectiveAction
    )

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Clear existing records in child-to-parent order to avoid FK errors
        for model in [
            CorrectiveAction, IncidentAlarmEvent, Incident,
            Acknowledgement, AlarmEvent, MachineStateEvent,
            Interlock, MachineSafetyZone, Machine, OperatorShift,
            SafetyZone, AlarmDefinition, Plant
        ]:
            db.query(model).delete()
        db.commit()

        # Insert in parent-to-child order
        model_order = [
            ("plants", Plant),
            ("safety_zones", SafetyZone),
            ("machines", Machine),
            ("machine_safety_zones", MachineSafetyZone),
            ("interlocks", Interlock),
            ("alarm_definitions", AlarmDefinition),
            ("operator_shifts", OperatorShift),
            ("machine_state_events", MachineStateEvent),
            ("alarm_events", AlarmEvent),
            ("acknowledgements", Acknowledgement),
            ("incidents", Incident),
            ("incident_alarm_events", IncidentAlarmEvent),
            ("corrective_actions", CorrectiveAction),
        ]

        for tbl_name, model_cls in model_order:
            records = datasets.get(tbl_name, [])
            if not records:
                continue
            # Batch insert in chunks of 5000 to manage memory
            chunk_size = 5000
            for i in range(0, len(records), chunk_size):
                chunk = records[i:i + chunk_size]
                db.bulk_insert_mappings(model_cls, chunk)
                db.commit()
            print(f"     Loaded {len(records)} records into {tbl_name}")

    except Exception as e:
        db.rollback()
        print(f"Error loading database: {e}")
        raise e
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Deterministic Industrial Safety Synthetic Data Generator")
    parser.add_argument("--seed", type=int, default=20261022, help="Deterministic random seed")
    parser.add_argument("--plants", type=int, default=4, help="Number of plants to generate")
    parser.add_argument("--machines", type=int, default=60, help="Number of machines to generate")
    parser.add_argument("--alarms", type=int, default=200, help="Number of alarm definitions to generate")
    parser.add_argument("--events", type=int, default=50000, help="Number of alarm events to generate")
    parser.add_argument("--days", type=int, default=30, help="Simulation duration in days")
    parser.add_argument("--load-db", action="store_true", help="Load generated data into database")

    args = parser.parse_args()

    config = GeneratorConfig(
        seed=args.seed,
        num_plants=args.plants,
        num_machines=args.machines,
        num_alarm_definitions=args.alarms,
        num_alarm_events=args.events,
        simulation_days=args.days,
    )

    run_pipeline(config, load_db=args.load_db)


if __name__ == "__main__":
    main()
