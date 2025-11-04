import { createContext, useContext, useMemo, useState } from 'react'
import type { WebMapFilter, WebMapState } from './types'
import { exportData } from './api'

export type WebMapPanel = 'filters' | 'layers' | null

export type WebMapContextValue = {
  state: WebMapState
  setState: (next: WebMapState) => void
  toggleLayer: (id: string) => void
  setFilter: (f: WebMapFilter) => void
  clearFilter: (id: string) => void
  openPanel: (panel: WebMapPanel) => void
  panel: WebMapPanel
  doExport: () => Promise<void>
}

const WebMapContext = createContext<WebMapContextValue | null>(null)

export function WebMapProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<WebMapState>({ layers: [], filters: [] })
  const [panel, setPanel] = useState<WebMapPanel>(null)

  const value = useMemo<WebMapContextValue>(() => ({
    state,
    setState: (next) => setState(next),
    toggleLayer: (id) => setState(s => ({
      ...s,
      layers: s.layers.map(l => l.id === id ? { ...l, enabled: !l.enabled } : l)
    })),
    setFilter: (f) => setState(s => {
      const existing = s.filters.findIndex(x => x.id === f.id)
      const filters = existing >= 0 ? s.filters.slice() : [...s.filters]
      if (existing >= 0) filters[existing] = f
      else filters.push(f)
      return { ...s, filters }
    }),
    clearFilter: (id) => setState(s => ({ ...s, filters: s.filters.filter(f => f.id !== id) })),
    openPanel: (p) => setPanel(p),
    panel,
    doExport: async () => {
      try {
        await exportData({ filters: state.filters, layers: state.layers.filter(l => l.enabled).map(l => l.id) })
      } catch (e) {
        console.error('Export failed', e)
      }
    }
  }), [state, panel])

  return <WebMapContext.Provider value={value}>{children}</WebMapContext.Provider>
}

export function useWebMap() {
  const ctx = useContext(WebMapContext)
  if (!ctx) throw new Error('useWebMap must be used within WebMapProvider')
  return ctx
}
