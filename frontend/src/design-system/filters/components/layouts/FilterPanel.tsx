import Icon from '@/components/ui/Icon'
import { useEffect } from 'react'
import { FilterComponent, FilterConfig, FilterSchema, FilterState, FilterGroup } from '../../types'
import TextFilter from '../primitives/TextFilter'
import NumberFilter from '../primitives/NumberFilter'
import SelectFilter from '../primitives/SelectFilter'
import DateRangeFilter from '../primitives/DateRangeFilter'
import SearchableSelect from '../primitives/SearchableSelect'
import NumberRangeFilter from '@/design-system/filters/components/primitives/NumberRangeFilter'
import { trackFilterApply, trackFilterChange, trackFilterReset } from '@/design-system/filters/utils/telemetry'

export interface FilterPanelProps {
  config: FilterConfig
  values: FilterState
  onChange: (field: string, value: unknown) => void
  onApply?: () => void
  onReset?: () => void
  className?: string
  onClose?: () => void
}

const registry: Record<FilterComponent, React.FC<{ schema: FilterSchema; value: unknown; onChange: (v: unknown) => void }>> = {
  [FilterComponent.TEXT_INPUT]: (p) => <TextFilter {...p} />,
  [FilterComponent.NUMBER_INPUT]: (p) => <NumberFilter {...p} />,
  [FilterComponent.SELECT]: (p) => <SelectFilter {...p} />,
  [FilterComponent.MULTI_SELECT]: (p) => <SelectFilter {...p} />,
  [FilterComponent.DATE_RANGE]: (p) => <DateRangeFilter {...p} />,
  [FilterComponent.SEARCHABLE_SELECT]: (p) => <SearchableSelect {...p} />,
  [FilterComponent.NUMBER_RANGE]: (p) => <NumberRangeFilter {...p} />,
}

export default function FilterPanel({ config, values, onChange, onApply, onReset, className, onClose }: FilterPanelProps) {
  useEffect(() => {
    try {
      const saved = localStorage.getItem('filters-collapsed')
      if (saved === '1') document.documentElement.classList.add('filters-collapsed')
    } catch { void 0 }
  }, [])
  const handleApply = () => {
    trackFilterApply(values)
    onApply && onApply()
  }
  const handleReset = () => {
    trackFilterReset()
    onReset && onReset()
  }
  return (
    <aside className={`filters-panel h-full flex flex-col border-l border-slate-200 bg-white dark:border-slate-800 dark:bg-[#0b1220] ${className || ''}`}>
      <div className="filters-header flex items-center justify-between px-3 py-3 border-b border-slate-200 dark:border-slate-800 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Icon name="Filter" className="text-slate-500 dark:text-slate-300" size={18} />
          <div className="filters-title text-sm font-bold text-slate-700 dark:text-slate-100">Filtros</div>
        </div>
        <div className="flex items-center gap-2">
          <button
            className="collapse-btn"
            aria-label="Recolher painel de filtros"
            aria-expanded="true"
            title="Recolher"
            onClick={(e) => {
              const next = document.documentElement.classList.toggle('filters-collapsed')
              e.currentTarget.setAttribute('aria-expanded', (!next).toString())
              try { localStorage.setItem('filters-collapsed', next ? '1' : '0') } catch { void 0 }
            }}
          >
            <Icon name="ChevronsLeft" size={18} className="icon-left" />
            <Icon name="ChevronsRight" size={18} className="icon-right" />
          </button>
          {onReset && (
            <button className="h-8 rounded-md border border-slate-300 px-2 text-xs font-semibold text-slate-700 hover:bg-slate-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800" onClick={handleReset}>
              Limpar
            </button>
          )}
          {onApply && (
            <button className="h-8 rounded-md bg-sky-600 px-3 text-xs font-bold text-white hover:bg-sky-700" onClick={handleApply}>
              Aplicar
            </button>
          )}
          {onClose && (
            <button aria-label="Fechar filtros" className="h-8 w-8 inline-flex items-center justify-center rounded-md border border-slate-300 hover:bg-slate-50 dark:border-slate-700 dark:hover:bg-slate-800" onClick={onClose}>
              <Icon name="X" size={14} className="text-slate-500" />
            </button>
          )}
        </div>
      </div>

      <div className="filters-content flex-1 overflow-y-auto px-3 py-3 flex flex-col gap-4">
        {config.groups.map((group: FilterGroup) => (
          <section key={group.id}>
            <div className="category-title mb-2 flex items-center gap-2">
              {group.icon && <Icon name={group.icon} size={14} className="text-slate-400" />}
              <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500">{group.label}</div>
            </div>
            <div className="flex flex-col gap-2">
              {group.filters.filter((f: FilterSchema) => !f.hidden).map((schema: FilterSchema) => {
                const Comp = schema.component ? registry[schema.component] : TextFilter
                const value = values?.[schema.field]
                return (
                  <div key={schema.id} className="filter-item">
                    <Comp
                      schema={schema}
                      value={value}
                      onChange={(v) => {
                        trackFilterChange(schema.field, v)
                        onChange(schema.field, v)
                      }}
                    />
                  </div>
                )}
              )}
            </div>
          </section>
        ))}
      </div>
    </aside>
  )
}
