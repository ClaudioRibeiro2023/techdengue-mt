import { useId } from 'react'
import { FilterOperator, FilterOption, FilterSchema } from '../../types'

export default function SelectFilter({ schema, value, onChange }: { schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }) {
  const uid = useId()
  const options: FilterOption[] = schema.options || []
  const multiple = schema.operator === FilterOperator.IN
  const id = `filter-${schema.id}-${uid}`
  const selectedValue: string | string[] = multiple
    ? (Array.isArray(value) ? (value as unknown[]).map((v) => String(v)) : [])
    : (value != null ? String(value) : '')

  return (
    <div className="flex flex-col gap-1">
      <label className="filter-label" htmlFor={id}>{schema.label}</label>
      <select
        id={id}
        name={schema.field}
        title={schema.label}
        aria-label={schema.label}
        multiple={multiple}
        className="min-h-9 rounded-md border border-slate-300 bg-white px-2 py-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
        value={selectedValue}
        onChange={(e) => {
          if (multiple) {
            const selected = Array.from(e.target.selectedOptions).map((o) => o.value)
            onChange(selected)
          } else {
            onChange(e.target.value === '' ? null : e.target.value)
          }
        }}
      >
        {!multiple && <option value="">{schema.placeholder || 'Selecione...'}</option>}
        {options.map((opt) => (
          <option key={String(opt.value)} value={String(opt.value)} disabled={opt.disabled}>
            {opt.label}
          </option>
        ))}
      </select>
      {schema.helpText && <div className="filter-help">{schema.helpText}</div>}
    </div>
  )
}
