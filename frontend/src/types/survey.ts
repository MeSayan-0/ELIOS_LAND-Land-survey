export type SurveyStatus = 'DRAFT'|'UPLOADING'|'PROCESSING'|'READY'|'REVIEW'|'FAILED'
export interface SurveyProject { id:string; parcelId?:string; status:SurveyStatus; createdAt?:string }
