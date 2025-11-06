import { useEffect, useState } from 'react'
import { useWebMap } from './context'
import { loadLayers } from './api'

export default function WebMapLayersPanel() {
  const { panel, openPanel, state, setState, toggleLayer } = useWebMap()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (panel !== 'layers' || state.layers.length > 0) return
    setLoading(true)
    loadLayers()
      .then(list => {
        setState({ ...state, layers: list.map(l => ({ id: l.id, name: l.name, group: l.group, enabled: true })) })
      })
      .catch(e => setError((e as Error).message))
      .finally(() => setLoading(false))
  }, [panel, state, setState])

  if (panel !== 'layers') return null

  return (
    <div className="fixed top-[64px] right-4 z-[930] w-[320px] max-w-[90vw] bg-white border border-gray-200 shadow-xl rounded-xl p-4">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-gray-800">Camadas</h3>
        <button onClick={() => openPanel(null)} className="px-2 py-1 text-xs border rounded-md hover:bg-gray-50">Fechar</button>
      </div>

      {loading && <div className="text-xs text-gray-500">Carregando camadas...</div>}
      {error && <div className="text-xs text-red-600">{error}</div>}

      {!loading && !error && (
        <div className="space-y-2 max-h-[50vh] overflow-auto pr-1">
          {state.layers.map(layer => (
            <label key={layer.id} className="flex items-center justify-between gap-2 text-sm">
              <div className="flex items-center gap-2">
                <input type="checkbox" checked={layer.enabled} onChange={() => toggleLayer(layer.id)} />
                <span className="font-medium text-gray-800">{layer.name}</span>
              </div>
            </label>
          ))}
        </div>
      )}
    </div>
  )
}
