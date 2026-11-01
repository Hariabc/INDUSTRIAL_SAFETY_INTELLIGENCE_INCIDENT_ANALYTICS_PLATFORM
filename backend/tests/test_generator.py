import os
import json
from generator.id_generator import IdGenerator


def test_id_generator_patterns():
    """Verify all deterministic ID patterns match platform specifications."""
    assert IdGenerator.plant_id(1) == "PLN-001"
    assert IdGenerator.machine_id(5) == "MCH-005"
    assert IdGenerator.safety_zone_id("PLN-001", 2) == "SAFE-PLN-001-002"
    assert IdGenerator.interlock_id("MCH-001", 1) == "ITL-MCH-001-001"
    assert IdGenerator.alarm_definition_id(10) == "DEF-010"
    assert IdGenerator.alarm_event_id("MCH-001", 42) == "ALM-MCH-001-000042"
    assert IdGenerator.operator_shift_id(1) == "SHF-000001"
    assert IdGenerator.incident_id(2026, 12) == "INC-2026-000012"
    assert IdGenerator.acknowledgement_id("ALM-MCH-001-000042", 1) == "ACK-ALM-MCH-001-000042-01"
    assert IdGenerator.corrective_action_id("INC-2026-000012", 1) == "ACT-INC-2026-000012-01"


def test_five_injected_anomaly_scenarios_labeled():
    """Verify that all 5 deliberate anomaly scenarios are present and isolated in ground truth."""
    gt_path = os.path.join("data", "ground_truth.json")
    assert os.path.exists(gt_path), "ground_truth.json must exist"

    with open(gt_path, "r", encoding="utf-8") as f:
        records = json.load(f)

    subtypes = set(r.get("subtype") for r in records)
    expected_subtypes = {
        "ACK_BEFORE_ALARM",
        "IMPOSSIBLE_INTERLOCK_STATE",
        "MISSING_TRIGGERING_ALARM",
        "REPLAYED_SOURCE_EVENT",
        "CLOSED_WITHOUT_VERIFICATION",
    }
    assert expected_subtypes.issubset(subtypes), f"Missing anomaly subtypes: {expected_subtypes - subtypes}"
    assert len(records) >= 100, f"Expected at least 100 injected anomalies, found {len(records)}"


def test_ground_truth_separation():
    """Ensure ground truth labels are strictly isolated from normal database feature columns."""
    from backend.app.models import AlarmEvent, Interlock, Incident, CorrectiveAction
    # Ensure neither AlarmEvent, Incident, nor CorrectiveAction have a column named 'ground_truth' or 'is_anomaly'
    for model in [AlarmEvent, Interlock, Incident, CorrectiveAction]:
        col_names = [c.name for c in model.__table__.columns]
        assert "ground_truth" not in col_names
        assert "is_anomaly" not in col_names
