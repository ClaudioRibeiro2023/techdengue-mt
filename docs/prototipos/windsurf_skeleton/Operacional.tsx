import React from 'react'
import { KPI } from '../components/KPI'
import { DataTable } from '../components/DataTable'

export const Operacional: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <KPI label="% SLA" value="92%" />
        <KPI label="Atividades/dia" value="128" />
        <KPI label="% Evidências válidas" value="99,4%" />
        <KPI label="Insumos usados" value="3.420" />
      </div>
      <DataTable
        columns={['Equipe', '%SLA', 'Atividades', 'Pendências']}
        rows={[['EQUIPE-A', '95%', 380, 3], ['EQUIPE-B', '90%', 330, 5]]}
      />
    </div>
  )
}
