import { useEffect, useMemo, useState } from 'react'
import { FilterConfig, FilterState } from '../types'
import { FilterEngine } from '../core/FilterEngine'
import { loadPersistedFilters, useFilterPersist } from './useFilterPersist'

interface UseFiltersOptions {
  config: FilterConfig
  data?: unknown[]
  initialValues?: FilterState
}

export function useFilters({ config, data = [], initialValues = {} }: UseFiltersOptions) {
  const persistCfg = typeof config.persist === 'boolean' ? { strategy: 'localStorage' as const, key: 'filters' } : config.persist
  const persisted = persistCfg ? loadPersistedFilters({ key: persistCfg.key, strategy: (persistCfg.strategy as 'localStorage' | 'url') || 'localStorage' }) : null

  const [filters, setFilters] = useState<FilterState>(persisted || initialValues)

  useFilterPersist(filters, { key: persistCfg?.key, strategy: (persistCfg?.strategy as 'localStorage' | 'url') || 'localStorage' })

  const schemas = useMemo(() => config.groups.flatMap((g) => g.filters), [config])

  const filteredData = useMemo(() => {
    if (!data?.length) return data
    return FilterEngine.apply(data, filters, schemas.map((s) => ({ field: s.field, operator: s.operator, dataType: s.dataType })))
  }, [data, filters, schemas])

  useEffect(() => {
    if (config.onChange) config.onChange(filters)
  }, [filters, config])

  return {
    filters,
    filteredData,
    setFilter: (field: string, value: unknown) => setFilters((prev) => ({ ...prev, [field]: value })),
    setFilters,
    reset: () => setFilters({}),
    clear: (field: string) => setFilters((prev) => { const n: Record<string, unknown> = { ...prev }; delete (n as Record<string, unknown>)[field]; return n as FilterState }),
    hasFilters: Object.keys(filters || {}).length > 0,
  }
}
