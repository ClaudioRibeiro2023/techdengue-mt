import { useEffect } from 'react'
import { FilterState } from '../types'

export function useFilterPersist(filters: FilterState, options?: { key?: string; strategy?: 'localStorage' | 'url' }) {
  const key = options?.key || 'filters'
  const strategy = options?.strategy || 'localStorage'

  useEffect(() => {
    if (!filters) return
    try {
      if (strategy === 'localStorage') {
        localStorage.setItem(key, JSON.stringify(filters))
      } else if (strategy === 'url') {
        const url = new URL(window.location.href)
        url.searchParams.set('filters', JSON.stringify(filters))
        window.history.replaceState({}, '', url.toString())
      }
    } catch { void 0 }
  }, [filters, key, strategy])
}

export function loadPersistedFilters(options?: { key?: string; strategy?: 'localStorage' | 'url' }): FilterState | null {
  const key = options?.key || 'filters'
  const strategy = options?.strategy || 'localStorage'
  try {
    if (strategy === 'localStorage') {
      const raw = localStorage.getItem(key)
      return raw ? (JSON.parse(raw) as FilterState) : null
    }
    if (strategy === 'url') {
      const params = new URLSearchParams(window.location.search)
      const raw = params.get('filters')
      return raw ? (JSON.parse(raw) as FilterState) : null
    }
  } catch { void 0 }
  return null
}
