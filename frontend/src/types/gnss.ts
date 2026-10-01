export type FixType = 'SINGLE'|'FLOAT'|'FIXED'|'UNKNOWN'
export interface FieldMeasurement { latitude:number; longitude:number; height?:number; accuracy?:number; fixType:FixType; timestamp:string; source:string }
