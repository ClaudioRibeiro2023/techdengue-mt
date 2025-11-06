import { useId } from 'react'
import { FilterSchema } from '../../types'

export default function TextFilter({ schema, value, onChange }: { schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }) {
  const uid = useId()
  const inputId = `filter-${schema.id}-${uid}`
  return (
    <div className="flex flex-col gap-1">
      <label className="filter-label" htmlFor={inputId}>{schema.label}</label>
      <input
        type="text"
        placeholder={schema.placeholder}
        className="h-9 rounded-md border border-slate-300 bg-white px-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
        id={inputId}
        value={(value as string) ?? ''}
        onChange={(e) => onChange(e.target.value)}
      />
      {schema.helpText && <div className="filter-help">{schema.helpText}</div>}
    </div>
  )
}
