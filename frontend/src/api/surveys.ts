import { apiFetch } from './client'

export interface Survey {
  id: string
  survey_code: string
  name: string
  parcel_id: string | null
  status: string
  description: string | null
}

export interface CreateSurveyPayload {
  survey_code: string
  name: string
  parcel_id?: string | null
  description?: string | null
}

export const getSurveys = () =>
  apiFetch<Survey[]>('/surveys')

export const createSurvey = (payload: CreateSurveyPayload) =>
  apiFetch<Survey>('/surveys', {
    method: 'POST',
    body: JSON.stringify(payload),
  })

export const getSurvey = (id: string) =>
  apiFetch<Survey>(`/surveys/${id}`)
