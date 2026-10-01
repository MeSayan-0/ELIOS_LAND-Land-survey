import { apiFetch } from './client'

export interface ProcessingArtifact {
  id: string
  survey_id: string
  processing_job_id: string | null
  artifact_type: string
  name: string
  storage_path: string
  file_format: string
  size_bytes: number
  created_at?: string
}

export interface OrthomosaicInfo {
  artifact_id: string
  name: string
  file_format: string
  size_bytes: number
  crs: string | null
  width: number
  height: number
  bands: number
  dtype: string[]
  resolution: [number, number]
  bounds: {
    left: number
    bottom: number
    right: number
    top: number
  }
}

export const getArtifacts = (surveyId: string) =>
  apiFetch<ProcessingArtifact[]>(
    `/surveys/${surveyId}/artifacts`
  )

export const getArtifact = (
  surveyId: string,
  artifactId: string
) =>
  apiFetch<ProcessingArtifact>(
    `/surveys/${surveyId}/artifacts/${artifactId}`
  )

export const getArtifactsByType = (
  surveyId: string,
  artifactType: string
) =>
  apiFetch<ProcessingArtifact[]>(
    `/surveys/${surveyId}/artifacts/type/${artifactType}`
  )

export const getOrthomosaicInfo = (surveyId: string) =>
  apiFetch<OrthomosaicInfo>(
    `/surveys/${surveyId}/orthomosaic/info`
  )

export const getOrthomosaicPreviewUrl = (surveyId: string) =>
  `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'}/surveys/${surveyId}/orthomosaic/preview`

export const getArtifactDownloadUrl = (
  surveyId: string,
  artifactId: string
) =>
  `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'}/surveys/${surveyId}/artifacts/${artifactId}/file`
