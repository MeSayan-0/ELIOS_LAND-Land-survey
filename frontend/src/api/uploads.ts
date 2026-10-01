import { apiFetch } from './client'

export interface SurveyFile {
  id: string
  survey_id: string
  filename: string
  file_type: string
  size_bytes: number
  sha256: string
  validation_status: string
  validation_message: string | null
  storage_path: string
}

export interface UploadSurveyFilesResponse {
  survey_id: string
  uploaded_count: number
  skipped_count: number
  uploaded: SurveyFile[]
  skipped: {
    filename: string | null
    reason: string
  }[]
}

export interface ValidateSurveyResponse {
  survey_id: string
  message: string
  total_files: number
  valid_files: number
  warning_files: number
  invalid_files: number
  image_count: number
}

export const uploadSurveyFiles = (
  surveyId: string,
  files: File[],
) => {
  const form = new FormData()

  files.forEach(file => {
    form.append('files', file)
  })

  return apiFetch<UploadSurveyFilesResponse>(
    `/surveys/${surveyId}/files`,
    {
      method: 'POST',
      body: form,
    },
  )
}

export const getSurveyFiles = (surveyId: string) =>
  apiFetch<SurveyFile[]>(
    `/surveys/${surveyId}/files`,
  )

export const validateSurveyData = (surveyId: string) =>
  apiFetch<ValidateSurveyResponse>(
    `/surveys/${surveyId}/validate/images`,
    {
      method: 'POST',
    },
  )
