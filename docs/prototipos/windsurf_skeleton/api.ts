export const API_BASE = '/v1';

export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(init?.headers || {}) },
    ...init
  })
  if (!res.ok) throw new Error(`HTTP ${res.status}`)
  return await res.json() as T
}

export function linkRelatorio(link?: { pdf_url?: string, csv_url?: string }) {
  return ({
    pdf: link?.pdf_url || '#',
    csv: link?.csv_url || '#'
  })
}
