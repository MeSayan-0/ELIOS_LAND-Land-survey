from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SurveyProject
from app.services.ingestion_service import register_survey_images


router = APIRouter(prefix="/surveys", tags=["Ingestion"])


@router.post("/{survey_id}/ingest/images")
def ingest_survey_images(
    survey_id: UUID,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    from pathlib import Path

    image_directory = (
        Path("storage")
        / "surveys"
        / survey.survey_code
        / "images"
    )

    try:
        result = register_survey_images(
            db=db,
            survey=survey,
            image_directory=image_directory,
        )
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return {
        "survey_id": str(survey.id),
        "survey_code": survey.survey_code,
        "message": "Survey images registered successfully.",
        **result,
    }
