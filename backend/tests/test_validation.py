from sqlalchemy.orm import Session
from backend.app.services.validation_service import DataValidationService


def test_data_validation_suite(db_session: Session):
    """Test full 10-point data validation suite execution."""
    val_service = DataValidationService(db_session)
    summary, findings = val_service.run_all_validations()

    assert summary["total_checks_performed"] == 10
    assert summary["overall_status"] == "PASSED"
    assert summary["data_integrity_score"] == 100.0
    assert summary["accidental_corruption_issues"] == 0
    assert summary["intentional_labeled_anomalies"] >= 100
    assert len(findings) > 0


def test_validation_distinguishes_intentional_anomalies(db_session: Session):
    """Ensure intentional anomalies are not flagged as accidental data corruption."""
    val_service = DataValidationService(db_session)
    _, findings = val_service.run_all_validations()

    for f in findings:
        if f["check_name"] in [
            "Acknowledgement Ordering",
            "Incident Traceability",
            "Corrective-Action Lifecycle",
            "Interlock State Validity",
            "Duplicate Event Fingerprints"
        ]:
            # All deliberate anomalies injected should be labeled as intentional
            assert f["is_intentional_anomaly"] is True
