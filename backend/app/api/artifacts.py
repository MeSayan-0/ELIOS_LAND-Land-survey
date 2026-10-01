from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.schemas import ProcessingArtifactResponse
from app.core.database import get_db
from app.models.processing_artifact import ProcessingArtifact
from app.models.survey import SurveyProject


router = APIRouter(
    prefix="/surveys/{survey_id}/artifacts",
    tags=["Processing Artifacts"],
)


@router.get(
    "",
    response_model=list[ProcessingArtifactResponse],
)
def list_artifacts(
    survey_id: UUID,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    statement = (
        select(ProcessingArtifact)
        .where(
            ProcessingArtifact.survey_id == survey_id
        )
        .order_by(
            ProcessingArtifact.created_at.asc()
        )
    )

    return db.scalars(statement).all()


@router.get(
    "/{artifact_id}",
    response_model=ProcessingArtifactResponse,
)
def get_artifact(
    survey_id: UUID,
    artifact_id: UUID,
    db: Session = Depends(get_db),
):
    artifact = db.scalar(
        select(ProcessingArtifact).where(
            ProcessingArtifact.id == artifact_id,
            ProcessingArtifact.survey_id == survey_id,
        )
    )

    if artifact is None:
        raise HTTPException(
            status_code=404,
            detail="Processing artifact not found.",
        )

    return artifact


@router.get(
    "/type/{artifact_type}",
    response_model=list[ProcessingArtifactResponse],
)
def list_artifacts_by_type(
    survey_id: UUID,
    artifact_type: str,
    db: Session = Depends(get_db),
):
    survey = db.get(SurveyProject, survey_id)

    if survey is None:
        raise HTTPException(
            status_code=404,
            detail="Survey not found.",
        )

    statement = (
        select(ProcessingArtifact)
        .where(
            ProcessingArtifact.survey_id == survey_id,
            ProcessingArtifact.artifact_type
            == artifact_type.upper(),
        )
        .order_by(
            ProcessingArtifact.created_at.asc()
        )
    )

    return db.scalars(statement).all()


@router.get(
    "/{artifact_id}/file",
)
def download_artifact(
    survey_id: UUID,
    artifact_id: UUID,
    db: Session = Depends(get_db),
):
    artifact = db.scalar(
        select(ProcessingArtifact).where(
            ProcessingArtifact.id == artifact_id,
            ProcessingArtifact.survey_id == survey_id,
        )
    )

    if artifact is None:
        raise HTTPException(
            status_code=404,
            detail="Processing artifact not found.",
        )

    path = Path(artifact.storage_path)

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail="Artifact file not found on storage.",
        )

    if not path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Artifact storage path is not a file.",
        )

    return FileResponse(
        path=path,
        filename=path.name,
        media_type="application/octet-stream",
    )
