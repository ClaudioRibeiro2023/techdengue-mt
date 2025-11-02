import React from 'react'
import { DataTable } from '../components/DataTable'

export const Admin: React.FC = () => {
  return (
    <div className="space-y-4">
      <div className="rounded-2xl border bg-white p-4">
        <div className="font-medium mb-2">Usuários (demo)</div>
        <DataTable columns={['Nome','E-mail','Papel','Escopo']}
          rows={[['Admin','admin@aeroengenharia.com','ADMIN','*']]} />
      </div>
    </div>
  )
}
