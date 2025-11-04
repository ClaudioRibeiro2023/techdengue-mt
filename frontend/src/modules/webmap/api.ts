import type { WebMapFilter } from './types'

export async function loadLayers(): Promise<Array<{ id: string; name: string; group?: string }>> {
  const res = await fetch('/api/webmap/layers')
  if (!res.ok) throw new Error('Failed to load layers')
  return res.json()
}

export async function exportData(payload: { filters: WebMapFilter[]; layers: string[] }): Promise<void> {
  const res = await fetch('/api/webmap/export', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) throw new Error('Export failed')
}
