import { useId } from 'react'
import { FilterSchema } from '../../types'

export default function DateRangeFilter({ schema, value, onChange }: { schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }) {
  const uid = useId()
  let start = '' as string
  let end = '' as string
  if (Array.isArray(value)) {
    const arr = value as unknown[]
    start = (arr[0] as string) ?? ''
    end = (arr[1] as string) ?? ''
  } else if (typeof value === 'object' && value) {
    const obj = value as Record<string, unknown>
    start = (obj['start'] as string) ?? (obj['0'] as string) ?? ''
    end = (obj['end'] as string) ?? (obj['1'] as string) ?? ''
  }
  const startId = `filter-${schema.id}-start-${uid}`
  const endId = `filter-${schema.id}-end-${uid}`
  return (
    <div className="flex flex-col gap-1">
      <label className="filter-label">{schema.label}</label>
      <div className="flex items-center gap-2">
        <input
          type="date"
          className="h-9 flex-1 rounded-md border border-slate-300 bg-white px-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
          id={startId}
          aria-label={`${schema.label} - início`}
          title={`${schema.label} - início`}
          placeholder="Início"
          value={start || ''}
          onChange={(e) => onChange([e.target.value || null, end || null])}
        />
        <span className="text-xs text-slate-400">até</span>
        <input
          type="date"
          className="h-9 flex-1 rounded-md border border-slate-300 bg-white px-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
          id={endId}
          aria-label={`${schema.label} - fim`}
          title={`${schema.label} - fim`}
          placeholder="Fim"
          value={end || ''}
          onChange={(e) => onChange([start || null, e.target.value || null])}
        />
      </div>
      {schema.helpText && <div className="filter-help">{schema.helpText}</div>}
    </div>
  )
}
