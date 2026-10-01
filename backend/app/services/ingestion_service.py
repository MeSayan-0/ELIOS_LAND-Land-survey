from hashlib import sha256
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SurveyFile, SurveyProject


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}


def calculate_sha256(path: Path) -> str:
    digest = sha256()

    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)

    return digest.hexdigest()


def register_survey_images(
    db: Session,
    survey: SurveyProject,
    image_directory: Path,
) -> dict:
    if not image_directory.exists():
        raise FileNotFoundError(
            f"Image directory does not exist: {image_directory}"
        )

    image_paths = sorted(
        path
        for path in image_directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    created = 0
    skipped = 0

    for path in image_paths:
        existing = db.scalar(
            select(SurveyFile).where(
                SurveyFile.survey_id == survey.id,
                SurveyFile.original_filename == path.name,
            )
        )

        if existing is not None:
            skipped += 1
            continue

        file_record = SurveyFile(
            survey_id=survey.id,
            original_filename=path.name,
            file_type="IMAGE",
            storage_path=str(path),
            size_bytes=path.stat().st_size,
            sha256=calculate_sha256(path),
            validation_status="PENDING",
        )

        db.add(file_record)
        created += 1

    db.commit()

    return {
        "created": created,
        "skipped": skipped,
        "total_images_found": len(image_paths),
    }
