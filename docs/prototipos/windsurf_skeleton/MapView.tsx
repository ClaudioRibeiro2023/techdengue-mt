import React from 'react'

// Placeholder do mapa (substituir por MapLibre/Leaflet conforme lib escolhida)
export const MapView: React.FC<{ title?: string }> = ({ title }) => {
  return (
    <div className="rounded-2xl border bg-white h-96 flex items-center justify-center text-slate-500">
      {title || 'Mapa (substituir por componente real)'}
    </div>
  )
}
