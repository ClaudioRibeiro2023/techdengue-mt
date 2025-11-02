import React from 'react'
import { UploadETL } from '../components/UploadETL'
import { DataTable } from '../components/DataTable'

export const ETL: React.FC = () => {
  return (
    <div className="space-y-4">
      <UploadETL />
      <DataTable
        columns={['Município', 'Casos', 'Inc/100k', 'Fonte']}
        rows={[['Belo Horizonte', 345, 13.8, 'SIVEP-ARBO']]}
      />
    </div>
  )
}
