import { apiFetch } from './client'
export const getCadastral = () => apiFetch('/api/cadastral')
export const importCadastral = (payload: unknown) => apiFetch('/api/cadastral/import', {method:'POST', body:JSON.stringify(payload)})
