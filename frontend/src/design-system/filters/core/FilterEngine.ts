import { DataType, FilterOperator, FilterState } from '../types'

export class FilterEngine {
  static apply<T = unknown>(
    data: T[],
    filters: FilterState,
    schemas: { field: string; operator: FilterOperator; dataType: DataType }[]
  ): T[] {
    if (!data || !schemas || !filters) return data
    const active = Object.keys(filters)
    if (active.length === 0) return data
    return data.filter((item) => this.matches(item, filters, schemas))
  }

  private static matches<T>(
    item: T,
    filters: FilterState,
    schemas: { field: string; operator: FilterOperator; dataType: DataType }[]
  ): boolean {
    return Object.entries(filters).every(([field, value]) => {
      const schema = schemas.find((s) => s.field === field)
      if (!schema) return true
      const val = this.get(item, schema.field)
      return this.op(val, value, schema.operator, schema.dataType)
    })
  }

  private static op(item: unknown, filter: unknown, operator: FilterOperator, dataType: DataType): boolean {
    if (operator === FilterOperator.CUSTOM) return true

    // Normalize strings for contains/starts/ends
    const asStr = (v: unknown) => (v == null ? '' : String(v))
    const asNum = (v: unknown) => {
      if (dataType === DataType.NUMBER) return Number(v)
      return Number(v)
    }

    switch (operator) {
      case FilterOperator.EQ: return item === filter
      case FilterOperator.NE: return item !== filter
      case FilterOperator.GT: return asNum(item) > asNum(filter)
      case FilterOperator.GTE: return asNum(item) >= asNum(filter)
      case FilterOperator.LT: return asNum(item) < asNum(filter)
      case FilterOperator.LTE: return asNum(item) <= asNum(filter)
      case FilterOperator.CONTAINS: return asStr(item).toLowerCase().includes(asStr(filter).toLowerCase())
      case FilterOperator.STARTS_WITH: return asStr(item).toLowerCase().startsWith(asStr(filter).toLowerCase())
      case FilterOperator.ENDS_WITH: return asStr(item).toLowerCase().endsWith(asStr(filter).toLowerCase())
      case FilterOperator.IN: return Array.isArray(filter) ? filter.includes(item as never) : false
      case FilterOperator.NOT_IN: return Array.isArray(filter) ? !filter.includes(item as never) : true
      case FilterOperator.BETWEEN: {
        const [min, max] = Array.isArray(filter) ? (filter as unknown[]) : [undefined, undefined]
        if (min == null || max == null) return true
        const n = asNum(item)
        return n >= asNum(min) && n <= asNum(max)
      }
      case FilterOperator.BEFORE: return new Date(item as string | number | Date) < new Date(filter as string | number | Date)
      case FilterOperator.AFTER: return new Date(item as string | number | Date) > new Date(filter as string | number | Date)
      case FilterOperator.DATE_RANGE: {
        const [start, end] = Array.isArray(filter) ? (filter as unknown[]) : [undefined, undefined]
        if (!start || !end) return true
        const d = new Date(item as string | number | Date).getTime()
        return d >= new Date(start as string | number | Date).getTime() && d <= new Date(end as string | number | Date).getTime()
      }
      case FilterOperator.IS_NULL: return item == null
      case FilterOperator.IS_NOT_NULL: return item != null
      case FilterOperator.IS_EMPTY: return item == null || (Array.isArray(item) ? item.length === 0 : String(item as unknown).length === 0)
      case FilterOperator.IS_NOT_EMPTY: return !(item == null || (Array.isArray(item) ? item.length === 0 : String(item as unknown).length === 0))
      default: return true
    }
  }

  private static get(obj: unknown, path: string): unknown {
    try {
      const parts = path.split('.')
      let current: unknown = obj
      for (const p of parts) {
        if (current == null || typeof current !== 'object') return undefined
        current = (current as Record<string, unknown>)[p]
      }
      return current
    } catch {
      return undefined
    }
  }

  static toURL(filters: FilterState): string {
    const params = new URLSearchParams()
    Object.entries(filters).forEach(([k, v]) => {
      if (v !== undefined && v !== null && !(Array.isArray(v) && v.length === 0)) {
        params.set(k, JSON.stringify(v))
      }
    })
    return params.toString()
  }

  static fromURL(queryString: string): FilterState {
    const params = new URLSearchParams(queryString.startsWith('?') ? queryString.slice(1) : queryString)
    const filters: FilterState = {}
    params.forEach((v, k) => {
      try { filters[k] = JSON.parse(v) } catch { filters[k] = v }
    })
    return filters
  }
}
