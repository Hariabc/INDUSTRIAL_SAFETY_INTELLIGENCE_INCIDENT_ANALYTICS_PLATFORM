from sqlalchemy.orm import Session
from backend.app.services.detection_engine import SafetyDetectionEngine
from backend.app.services.evaluation_service import ModelEvaluationService


def test_detection_engine_execution(db_session: Session):
    """Test that all 8 rules execute and populate explainable safety anomalies."""
    engine = SafetyDetectionEngine(db_session)
    detections = engine.run_all_rules(persist_to_db=False)

    assert len(detections) > 0, "Detection engine should identify anomalies"

    detected_types = set(d.anomaly_type for d in detections)
    expected_rules = {
        "REPEATED_UNSAFE_CONDITION",
        "DELAYED_ACKNOWLEDGEMENT",
        "ALARM_FLOOD",
        "NUISANCE_ALARM",
        "INTERLOCK_VIOLATION",
        "MISSING_INCIDENT_CONTEXT",
        "DUPLICATE_ALARM_REPLAY",
        "INCOMPLETE_CORRECTIVE_ACTION",
    }
    assert expected_rules.issubset(detected_types), f"Missing detection rules: {expected_rules - detected_types}"

    # Verify explainability fields
    for d in detections[:20]:
        assert d.id.startswith("ANM-"), f"Invalid anomaly ID: {d.id}"
        assert len(d.explanation) > 10, "Explanation must be descriptive"
        assert len(d.recommended_action) > 10, "Recommended action must be actionable"
        assert d.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]


def test_model_evaluation_metrics(db_session: Session):
    """Verify precision, recall, F1, and dynamic operational KPI calculations."""
    eval_svc = ModelEvaluationService(db_session)
    res = eval_svc.evaluate()

    perf = res["model_performance"]
    assert perf["precision"] >= 0.90, f"Precision lower than expected: {perf['precision']}"
    assert perf["recall"] >= 0.90, f"Recall lower than expected: {perf['recall']}"
    assert perf["f1_score"] >= 0.90, f"F1 score lower than expected: {perf['f1_score']}"
    assert perf["true_positives"] > 0
    assert perf["ground_truth_total"] >= 100

    kpis = res["operational_kpis"]
    assert kpis["total_alarms"] >= 50000
    assert kpis["critical_alarms"] > 0
    assert kpis["active_incidents"] > 0
    assert kpis["avg_acknowledgement_time_seconds"] > 0
    assert kpis["data_integrity_score"] == 100.0
