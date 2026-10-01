from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import SurveyCreate, SurveyResponse
from app.core.database import get_db
from app.models import SurveyProject


router = APIRouter(
    prefix="/surveys",
    tags=["Surveys"],
)


@router.post(
    "",
    response_model=SurveyResponse,
    status_code=201,
)
def create_survey(
    payload: SurveyCreate,
    db: Session = Depends(get_db),
):
    existing = db.scalar(
        select(SurveyProject).where(
            SurveyProject.survey_code == payload.survey_code
        )
    )

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Survey code already exists.",
        )

    survey = SurveyProject(
        survey_code=payload.survey_code,
        name=payload.name,
        parcel_id=payload.parcel_id,
        description=payload.description,
        status="DRAFT",
    )

    db.add(survey)
    db.commit()
    db.refresh(survey)

    return survey


@router.get(
    "",
    response_model=list[SurveyResponse],
)
def list_surveys(
    db: Session = Depends(get_db),
):
    statement = select(SurveyProject).order_by(
        SurveyProject.created_at.desc()
    )

    return list(db.scalars(statement).all())


@router.get(
    "/{survey_id}",
    response_model=SurveyResponse,
)
def get_survey(
    survey_id: UUID,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    return survey
