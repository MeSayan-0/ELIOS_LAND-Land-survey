from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import SurveyFile
from app.services.validation_service import validate_file


def validate_survey_images(
    db: Session,
    survey_id,
) -> dict:
    statement = (
        select(SurveyFile)
        .where(
            SurveyFile.survey_id == survey_id,
            SurveyFile.file_type == "IMAGE",
        )
        .order_by(SurveyFile.original_filename)
    )

    files = db.scalars(statement).all()

    counts = {
        "VALID": 0,
        "INVALID": 0,
        "WARNING": 0,
        "PENDING": 0,
    }

    for survey_file in files:
        status, message = validate_file(
            survey_file.storage_path,
            survey_file.file_type,
        )

        survey_file.validation_status = status
        survey_file.validation_message = message

        counts[status] = counts.get(status, 0) + 1

    db.commit()

    return {
        "total": len(files),
        "valid": counts["VALID"],
        "invalid": counts["INVALID"],
        "warning": counts["WARNING"],
        "pending": counts["PENDING"],
    }
