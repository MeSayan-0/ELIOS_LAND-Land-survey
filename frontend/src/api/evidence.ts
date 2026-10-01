import { apiFetch } from './client'
export const generateEvidence = (payload: unknown) => apiFetch('/evidence/generate', {method:'POST', body:JSON.stringify(payload)})
export const getManifest = (id: string) => apiFetch(`/evidence/${id}/manifest`)
