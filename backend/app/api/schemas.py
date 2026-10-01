from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SurveyCreate(BaseModel):
    survey_code: str
    name: str
    parcel_id: str | None = None
    description: str | None = None


class SurveyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    survey_code: str
    name: str
    parcel_id: str | None
    status: str
    description: str | None


class ProcessingArtifactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    survey_id: UUID
    processing_job_id: UUID | None
    artifact_type: str
    name: str
    storage_path: str
    file_format: str
    size_bytes: int
