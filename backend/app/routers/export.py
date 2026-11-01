import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

router = APIRouter(prefix="/export", tags=["Data Export"])


@router.get("/{entity}")
def export_entity_data(
    entity: str,
    format: str = Query("csv", pattern="^(csv|json)$")
):
    """Download exported CSV or JSON dataset for any system entity."""
    clean_entity = entity.lower().strip()

    # Handle special reports
    if clean_entity == "ground_truth":
        file_path = os.path.join("data", f"ground_truth.{format}")
    elif clean_entity == "validation_report":
        file_path = os.path.join("data", f"validation_report.{format}")
    elif clean_entity == "validation_summary":
        file_path = os.path.join("data", "validation_summary.json")
    elif clean_entity == "manifest":
        file_path = os.path.join("data", "source_manifest.json")
    else:
        # Entity table exports
        folder = "csv" if format == "csv" else "json"
        file_path = os.path.join("data", "exports", folder, f"{clean_entity}.{format}")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Export file for '{entity}' ({format}) not found on disk.")

    media_type = "text/csv" if format == "csv" else "application/json"
    filename = f"{clean_entity}.{format}"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename,
    )
