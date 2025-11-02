import React from 'react'
import { KPI } from '../components/KPI'
import { MapView } from '../components/MapView'

export const Mapa: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <KPI label="Incidência/100k" value="13,8" hint="Competência: 2025-09" />
        <KPI label="Casos" value="345" />
        <KPI label="IPO" value="1,2" />
        <KPI label="Cobertura" value="85%" />
      </div>
      <MapView title="Mapa de Incidência (choropleth)"/>
    </div>
  )
}
