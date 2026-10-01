export type JobStatus = 'QUEUED'|'RUNNING'|'COMPLETED'|'FAILED'
export interface ProcessingJob { id:string; type:string; status:JobStatus; progress?:number; message?:string }
