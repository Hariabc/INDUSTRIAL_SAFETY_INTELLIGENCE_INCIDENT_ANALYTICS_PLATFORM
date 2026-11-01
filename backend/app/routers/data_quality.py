import os
import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.validation_service import DataValidationService

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])


@router.get("")
def get_data_quality_report(db: Session = Depends(get_db)):
    """Retrieve full data quality evaluation report across 10 validation points."""
    summary_path = os.path.join("data", "validation_summary.json")
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
        except Exception:
            service = DataValidationService(db)
            summary, _ = service.run_all_validations()
    else:
        service = DataValidationService(db)
        summary, _ = service.run_all_validations()

    # Load top findings from report if exists
    findings = []
    report_csv = os.path.join("data", "validation_report.csv")
    if os.path.exists(report_csv):
        import csv
        try:
            with open(report_csv, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                findings = [row for i, row in enumerate(reader) if i < 30]
        except Exception:
            pass

    return {
        "summary": summary,
        "sample_findings": findings,
    }


@router.post("/validate")
def run_data_validation(db: Session = Depends(get_db)):
    """Trigger a live validation run across all 10 checks."""
    service = DataValidationService(db)
    summary, findings = service.run_all_validations()
    return {
        "message": "Validation complete",
        "summary": summary,
        "total_findings": len(findings),
    }
