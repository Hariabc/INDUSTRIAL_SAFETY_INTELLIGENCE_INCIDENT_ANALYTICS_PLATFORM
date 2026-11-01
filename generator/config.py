from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class GeneratorConfig:
    seed: int = 20261022
    num_plants: int = 4
    num_machines: int = 60
    num_alarm_definitions: int = 200
    num_alarm_events: int = 50000
    simulation_days: int = 30
    start_date: datetime = datetime(2026, 10, 1, 0, 0, 0)

    # Injected anomaly counts for deterministic evaluation
    num_ack_before_alarm: int = 25
    num_impossible_interlock: int = 20
    num_missing_incident_context: int = 15
    num_duplicate_alarm_replay: int = 35
    num_action_closed_unverified: int = 20

    @property
    def end_date(self) -> datetime:
        return self.start_date + timedelta(days=self.simulation_days)
