import { apiFetch } from './client'
export const runBoundaryAI = (surveyId: string) => apiFetch(`/surveys/${surveyId}/boundary/ai`, {method:'POST'})
export const saveBoundaryVersion = (surveyId: string, payload: unknown) => apiFetch(`/surveys/${surveyId}/boundary`, {method:'POST', body:JSON.stringify(payload)})
