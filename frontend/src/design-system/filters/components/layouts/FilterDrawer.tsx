import FilterPanel, { FilterPanelProps } from './FilterPanel'

export default function FilterDrawer({ open, onClose, ...panel }: FilterPanelProps & { open: boolean; onClose: () => void }) {
  return (
    <div
      className={`filters-drawer-root fixed left-0 right-0 z-[1000] ${open ? '' : 'pointer-events-none'}`}
      role="dialog"
      aria-modal="true"
    >
      <div
        className={`absolute inset-0 bg-transparent backdrop-blur-0 transition-opacity ${open ? 'opacity-100' : 'opacity-0'}`}
        onClick={onClose}
      />
      <div
        className={`filters-panel-body absolute right-0 top-0 h-full translate-x-0 bg-white shadow-md transition-transform dark:bg-[#0b1220] ${
          open ? 'translate-x-0' : 'translate-x-full'
        } rounded-none border-l border-[#e2e8f0] dark:border-slate-800 flex flex-col`}
      >
        <FilterPanel {...panel} onClose={onClose} />
      </div>
    </div>
  )
}
