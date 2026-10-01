import { apiFetch } from './client'

export interface ProcessingJob {
  id: string
  survey_id: string
  job_type: string
  status: string
  progress: number
  message: string | null
  started_at: string | null
  completed_at: string | null
  error_message: string | null
}

export const startPPK = (surveyId: string) =>
  apiFetch<ProcessingJob>(
    `/surveys/${surveyId}/processing?job_type=PPK`,
    { method: 'POST' }
  )

export const startOrthomosaic = (surveyId: string) =>
  apiFetch<ProcessingJob>(
    `/surveys/${surveyId}/processing?job_type=ORTHOMOSAIC`,
    { method: 'POST' }
  )

export const getJob = (surveyId: string, jobId: string) =>
  apiFetch<ProcessingJob>(
    `/surveys/${surveyId}/processing/${jobId}`
  )

export const getProcessingJobs = (surveyId: string) =>
  apiFetch<ProcessingJob[]>(
    `/surveys/${surveyId}/processing`
  )
