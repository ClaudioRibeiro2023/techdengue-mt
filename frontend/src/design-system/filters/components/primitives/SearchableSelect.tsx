import { useEffect, useMemo, useRef, useState, useId } from 'react'
import { FilterOperator, FilterOption, FilterSchema } from '../../types'
const cacheStore = new Map<string, { expires: number; options: FilterOption[] }>()

async function fetchOptions(schema: FilterSchema): Promise<FilterOption[]> {
  const src = schema.optionsSource
  if (src?.fetch) {
    const r = await src.fetch()
    return r as FilterOption[]
  }
  if (src?.type === 'api' && src.endpoint) {
    const key = JSON.stringify({ endpoint: src.endpoint, params: src.params })
    const now = Date.now()
    const ttl = typeof src.cacheTTL === 'number' ? src.cacheTTL : 30000
    if (src.cache && cacheStore.has(key)) {
      const item = cacheStore.get(key)!
      if (item.expires > now) return item.options
    }
    const url = new URL(src.endpoint, window.location.origin)
    if (src.params) {
      Object.entries(src.params).forEach(([k, v]) => v != null && url.searchParams.set(k, String(v)))
    }
    const res = await fetch(url.toString(), { method: src.method || 'GET' })
    const data = await res.json()
    const transformed = src.transform ? src.transform(data) : (data as FilterOption[])
    if (src.cache) cacheStore.set(key, { expires: now + ttl, options: transformed })
    return transformed
  }
  return schema.options || []
}

export default function SearchableSelect({ schema, value, onChange }: { schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }) {
  const uid = useId()
  const id = `filter-${schema.id}-${uid}`
  const [query, setQuery] = useState('')
  const [options, setOptions] = useState<FilterOption[]>(schema.options || [])
  const [loading, setLoading] = useState(false)
  const multiple = schema.operator === FilterOperator.IN
  const mounted = useRef(false)

  useEffect(() => {
    mounted.current = true
    const load = async () => {
      try {
        setLoading(true)
        const opts = await fetchOptions(schema)
        if (mounted.current) setOptions(opts)
      } finally {
        if (mounted.current) setLoading(false)
      }
    }
    if (schema.optionsSource) void load()
    return () => { mounted.current = false }
  }, [schema])

  const filtered = useMemo(() => {
    if (!query) return options
    const q = query.toLowerCase()
    return options.filter(o => o.label.toLowerCase().includes(q))
  }, [options, query])

  const selectedValue: string | string[] = multiple
    ? (Array.isArray(value) ? (value as unknown[]).map(v => String(v)) : [])
    : (value != null ? String(value) : '')

  return (
    <div className="flex flex-col gap-1">
      <label className="filter-label" htmlFor={id}>{schema.label}</label>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder={schema.placeholder || 'Buscar...'}
        className="h-8 rounded-md border border-slate-300 bg-white px-2 text-xs outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
        aria-label={`${schema.label} - busca`}
      />
      <select
        id={id}
        name={schema.field}
        multiple={multiple}
        value={selectedValue}
        onChange={(e) => {
          if (multiple) {
            const vals = Array.from(e.currentTarget.selectedOptions).map(o => o.value)
            onChange(vals)
          } else {
            onChange(e.currentTarget.value)
          }
        }}
        className="min-h-9 rounded-md border border-slate-300 bg-white px-2 py-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
        aria-label={schema.label}
        title={schema.label}
      >
        {!multiple && <option value="">Selecione...</option>}
        {loading && <option disabled>Carregando...</option>}
        {!loading && filtered.map((opt) => (
          <option key={String(opt.value)} value={String(opt.value)} disabled={opt.disabled}>
            {opt.label}
          </option>
        ))}
      </select>
      {schema.helpText && <div className="filter-help">{schema.helpText}</div>}
    </div>
  )
}
