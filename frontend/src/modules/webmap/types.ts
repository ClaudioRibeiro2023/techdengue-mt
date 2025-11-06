export type WebMapLayer = {
  id: string
  name: string
  enabled: boolean
  group?: string
  opacity?: number
}

export type WebMapFilter = {
  id: string
  field: string
  op: 'eq' | 'neq' | 'gt' | 'gte' | 'lt' | 'lte' | 'in' | 'between' | 'ilike'
  value: string | number | boolean | Array<string | number> | { min: string | number; max: string | number }
}

export type WebMapState = {
  layers: WebMapLayer[]
  filters: WebMapFilter[]
  bbox?: [number, number, number, number]
  timeRange?: [string, string]
}
