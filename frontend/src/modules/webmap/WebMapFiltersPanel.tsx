import { useState } from 'react'
import { useWebMap } from './context'

export default function WebMapFiltersPanel() {
  const { panel, openPanel, setFilter, clearFilter, state } = useWebMap()
  const [from, setFrom] = useState('')
  const [to, setTo] = useState('')
  const [municipios, setMunicipios] = useState('')

  if (panel !== 'filters') return null

  return (
    <div className="fixed top-[64px] right-4 z-[930] w-[320px] max-w-[90vw] bg-white border border-gray-200 shadow-xl rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800">Filtros do Mapa</h3>
        <button onClick={() => openPanel(null)} className="px-2 py-1 text-xs border rounded-md hover:bg-gray-50">Fechar</button>
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Período (data)</label>
          <div className="flex gap-2">
            <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} className="flex-1 border rounded-md px-2 py-1 text-sm" aria-label="Data inicial" title="Data inicial" />
            <input type="date" value={to} onChange={(e) => setTo(e.target.value)} className="flex-1 border rounded-md px-2 py-1 text-sm" aria-label="Data final" title="Data final" />
          </div>
          <div className="mt-2 flex gap-2">
            <button
              className="px-3 py-1.5 text-xs rounded-md border border-gray-200 hover:bg-gray-50"
              onClick={() => {
                if (from && to) setFilter({ id: 'periodo', field: 'data', op: 'between', value: { min: from, max: to } })
              }}
            >Aplicar</button>
            <button className="px-3 py-1.5 text-xs rounded-md border border-gray-200 hover:bg-gray-50" onClick={() => clearFilter('periodo')}>Limpar</button>
          </div>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Municípios (códigos IBGE separados por vírgula)</label>
          <input type="text" value={municipios} onChange={(e) => setMunicipios(e.target.value)} placeholder="5103403,5107909" className="w-full border rounded-md px-2 py-1 text-sm" />
          <div className="mt-2 flex gap-2">
            <button
              className="px-3 py-1.5 text-xs rounded-md border border-gray-200 hover:bg-gray-50"
              onClick={() => {
                const arr = municipios.split(',').map(s => s.trim()).filter(Boolean)
                if (arr.length) setFilter({ id: 'municipios', field: 'cod_mun', op: 'in', value: arr })
              }}
            >Aplicar</button>
            <button className="px-3 py-1.5 text-xs rounded-md border border-gray-200 hover:bg-gray-50" onClick={() => clearFilter('municipios')}>Limpar</button>
          </div>
        </div>

        {state.filters.length > 0 && (
          <div className="pt-2 border-t">
            <div className="text-xs text-gray-500">Ativos: {state.filters.length}</div>
          </div>
        )}
      </div>
    </div>
  )
}
