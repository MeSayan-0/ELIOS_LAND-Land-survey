import hashlib
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models import SurveyFile, SurveyProject
from app.services.validation_service import validate_file


router = APIRouter(
    prefix="/surveys",
    tags=["Survey Files"],
)


def calculate_sha256(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def detect_file_type(filename: str) -> str:
    extension = Path(filename).suffix.lower()

    mapping = {
        ".jpg": "IMAGE",
        ".jpeg": "IMAGE",
        ".png": "IMAGE",
        ".tif": "RASTER",
        ".tiff": "RASTER",
        ".csv": "CSV",
        ".txt": "TEXT",
        ".log": "FLIGHT_LOG",
        ".bin": "FLIGHT_LOG",
        ".obs": "GNSS_OBSERVATION",
        ".nav": "GNSS_NAVIGATION",
        ".rnx": "GNSS_RINEX",
        ".zip": "ARCHIVE",
        ".json": "JSON",
        ".kml": "KML",
        ".kmz": "KMZ",
        ".las": "POINT_CLOUD",
        ".laz": "POINT_CLOUD",
    }

    return mapping.get(extension, "OTHER")


def serialize_survey_file(survey_file: SurveyFile) -> dict:
    return {
        "id": str(survey_file.id),
        "survey_id": str(survey_file.survey_id),
        "filename": survey_file.original_filename,
        "file_type": survey_file.file_type,
        "size_bytes": survey_file.size_bytes,
        "sha256": survey_file.sha256,
        "validation_status": survey_file.validation_status,
        "validation_message": survey_file.validation_message,
        "storage_path": survey_file.storage_path,
    }


@router.post("/{survey_id}/files")
async def upload_survey_files(
    survey_id: UUID,
    files: list[UploadFile] = File(...),
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files were uploaded.",
        )

    survey_dir = (
        Path(settings.storage_root)
        / "surveys"
        / survey.survey_code
    )

    survey_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    uploaded_files = []
    skipped_files = []

    try:
        for file in files:
            if not file.filename:
                skipped_files.append({
                    "filename": None,
                    "reason": "Uploaded file has no filename.",
                })
                continue

            safe_filename = Path(file.filename).name
            destination = survey_dir / safe_filename

            if destination.exists():
                skipped_files.append({
                    "filename": safe_filename,
                    "reason": "A file with this name already exists for this survey.",
                })
                continue

            size_bytes = 0

            with destination.open("wb") as output:
                while True:
                    chunk = await file.read(1024 * 1024)

                    if not chunk:
                        break

                    output.write(chunk)
                    size_bytes += len(chunk)

            sha256 = calculate_sha256(destination)

            survey_file = SurveyFile(
                survey_id=survey.id,
                original_filename=safe_filename,
                file_type=detect_file_type(safe_filename),
                storage_path=str(destination),
                size_bytes=size_bytes,
                sha256=sha256,
                validation_status="PENDING",
                validation_message=None,
            )

            db.add(survey_file)
            uploaded_files.append(survey_file)

        db.commit()

        for survey_file in uploaded_files:
            db.refresh(survey_file)

    except Exception:
        db.rollback()
        raise

    return {
        "survey_id": str(survey.id),
        "uploaded_count": len(uploaded_files),
        "skipped_count": len(skipped_files),
        "uploaded": [
            serialize_survey_file(item)
            for item in uploaded_files
        ],
        "skipped": skipped_files,
    }


@router.get("/{survey_id}/files")
def list_survey_files(
    survey_id: UUID,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    files = (
        db.query(SurveyFile)
        .filter(SurveyFile.survey_id == survey_id)
        .order_by(SurveyFile.uploaded_at.desc())
        .all()
    )

    return [
        serialize_survey_file(item)
        for item in files
    ]


@router.post("/{survey_id}/files/{file_id}/validate")
def validate_survey_file(
    survey_id: UUID,
    file_id: UUID,
    db: Session = Depends(get_db),
):
    survey_file = db.get(SurveyFile, file_id)

    if survey_file is None or survey_file.survey_id != survey_id:
        raise HTTPException(
            status_code=404,
            detail="Survey file not found.",
        )

    status, message = validate_file(
        survey_file.storage_path,
        survey_file.file_type,
    )

    survey_file.validation_status = status
    survey_file.validation_message = message

    db.commit()
    db.refresh(survey_file)

    return serialize_survey_file(survey_file)
