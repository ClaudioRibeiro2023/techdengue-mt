import { FilterState } from '../types'

export type QueryValue = string | number | boolean | Array<string | number | boolean>

export type MappingRule =
  | string
  | {
      to: string
      transform?: (value: unknown) => QueryValue | null | undefined
      when?: (value: unknown) => boolean
    }

export type QueryMapping = Record<string, MappingRule>

const isEmpty = (v: unknown) => v == null || v === '' || (Array.isArray(v) && v.length === 0)

export function buildQuery(
  filters: FilterState | Record<string, unknown>,
  mapping: QueryMapping,
  opts?: { dropEmpty?: boolean }
): URLSearchParams {
  const params = new URLSearchParams()
  const dropEmpty = opts?.dropEmpty !== false

  Object.entries(mapping).forEach(([fromKey, rule]) => {
    const raw = (filters as Record<string, unknown>)[fromKey]
    const toKey = typeof rule === 'string' ? rule : rule.to
    const transformed = typeof rule === 'string' ? (raw as unknown) : (rule.transform ? rule.transform(raw) : raw)
    const shouldInclude = typeof rule === 'string' ? true : (rule.when ? rule.when(raw) : true)

    if (!shouldInclude) return
    if (dropEmpty && isEmpty(transformed)) return

    if (Array.isArray(transformed)) {
      // padrão: CSV
      params.set(toKey, transformed.map((v) => String(v)).join(','))
    } else if (typeof transformed === 'boolean' || typeof transformed === 'number' || typeof transformed === 'string') {
      params.set(toKey, String(transformed))
    } else if (transformed != null) {
      params.set(toKey, String(transformed))
    }
  })

  return params
}
