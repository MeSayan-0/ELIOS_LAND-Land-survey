from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models import SurveyProject
from app.services.bulk_validation_service import validate_survey_images


router = APIRouter(prefix="/surveys", tags=["Validation"])


@router.post("/{survey_id}/validate/images")
def validate_images(
    survey_id: UUID,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    result = validate_survey_images(
        db=db,
        survey_id=survey_id,
    )

    return {
        "survey_id": str(survey_id),
        "message": "Survey images validated.",
        **result,
    }
