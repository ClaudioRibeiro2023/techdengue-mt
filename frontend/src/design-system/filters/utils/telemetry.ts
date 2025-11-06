import type { FilterState } from '../types'

const KEY = 'filters_telemetry'

type TelemetryStore = {
  applies: number
  resets: number
  changes: Record<string, { count: number; last: unknown }>
}

function load(): TelemetryStore {
  try {
    const raw = localStorage.getItem(KEY)
    if (!raw) return { applies: 0, resets: 0, changes: {} }
    const parsed = JSON.parse(raw) as TelemetryStore
    return parsed || { applies: 0, resets: 0, changes: {} }
  } catch {
    return { applies: 0, resets: 0, changes: {} }
  }
}

function save(data: TelemetryStore) {
  try { localStorage.setItem(KEY, JSON.stringify(data)) } catch { void 0 }
}

export function trackFilterChange(field: string, value: unknown) {
  const store = load()
  const cur = store.changes[field] || { count: 0, last: undefined }
  store.changes[field] = { count: cur.count + 1, last: value }
  save(store)
  try { console.info('[filters] change', { field, value }) } catch { void 0 }
}

export function trackFilterApply(values: FilterState) {
  const store = load()
  store.applies += 1
  save(store)
  try { console.info('[filters] apply', values) } catch { void 0 }
}

export function trackFilterReset() {
  const store = load()
  store.resets += 1
  save(store)
  try { console.info('[filters] reset') } catch { void 0 }
}

export function getFilterTelemetry(): TelemetryStore {
  return load()
}
