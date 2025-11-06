import { useId } from 'react'
import { FilterSchema } from '../../types'

export default function NumberRangeFilter({ schema, value, onChange }: { schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }) {
  const uid = useId()
  const minId = `filter-${schema.id}-min-${uid}`
  const maxId = `filter-${schema.id}-max-${uid}`

  const arr = Array.isArray(value) ? (value as unknown[]) : [undefined, undefined]
  const min = arr[0] as number | string | undefined
  const max = arr[1] as number | string | undefined

  const asNum = (v: unknown, def: number) => (v == null || v === '' ? def : Number(v))
  const useSlider = Boolean((schema.metadata as Record<string, unknown> | undefined)?.['slider'])
  const sliderMin = asNum((schema.metadata as Record<string, unknown> | undefined)?.['min'], 0)
  const sliderMax = asNum((schema.metadata as Record<string, unknown> | undefined)?.['max'], 100)
  const sliderStep = asNum((schema.metadata as Record<string, unknown> | undefined)?.['step'], 1)

  return (
    <div className="flex flex-col gap-1">
      <label className="filter-label">{schema.label}</label>
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <label htmlFor={minId} className="sr-only">Mínimo</label>
          {useSlider ? (
            <input
              id={minId}
              type="range"
              min={sliderMin}
              max={sliderMax}
              step={sliderStep}
              value={min != null && min !== '' ? Number(min) : sliderMin}
              onChange={(e) => {
                const nextMin = Number(e.currentTarget.value)
                onChange([nextMin, max != null && max !== '' ? Number(max) : sliderMax])
              }}
              className="w-full"
              aria-label="Mínimo"
            />
          ) : (
            <input
              id={minId}
              type="number"
              placeholder={schema.placeholder || 'Mín'}
              className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
              value={min != null && min !== '' ? String(min) : ''}
              onChange={(e) => {
                const nextMin = e.currentTarget.value === '' ? undefined : Number(e.currentTarget.value)
                onChange([nextMin, max])
              }}
            />
          )}
        </div>
        <span className="text-slate-400 text-xs">—</span>
        <div className="flex-1">
          <label htmlFor={maxId} className="sr-only">Máximo</label>
          {useSlider ? (
            <input
              id={maxId}
              type="range"
              min={sliderMin}
              max={sliderMax}
              step={sliderStep}
              value={max != null && max !== '' ? Number(max) : sliderMax}
              onChange={(e) => {
                const nextMax = Number(e.currentTarget.value)
                onChange([min != null && min !== '' ? Number(min) : sliderMin, nextMax])
              }}
              className="w-full"
              aria-label="Máximo"
            />
          ) : (
            <input
              id={maxId}
              type="number"
              placeholder={schema.placeholder || 'Máx'}
              className="h-9 w-full rounded-md border border-slate-300 bg-white px-2 text-sm outline-none focus:border-slate-400 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100 dark:focus:border-slate-600"
              value={max != null && max !== '' ? String(max) : ''}
              onChange={(e) => {
                const nextMax = e.currentTarget.value === '' ? undefined : Number(e.currentTarget.value)
                onChange([min, nextMax])
              }}
            />
          )}
        </div>
      </div>
      {schema.helpText && <div className="filter-help">{schema.helpText}</div>}
    </div>
  )
}
