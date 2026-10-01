export type BoundarySource = 'AI'|'HUMAN'|'AI_HUMAN'
export interface BoundaryVersion { id:string; source:BoundarySource; version:number; confidence?:number }
