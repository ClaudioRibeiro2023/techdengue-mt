import React, { useState } from 'react'
import { api } from '../lib/api'

export const UploadETL: React.FC = () => {
  const [file, setFile] = useState<File | null>(null)
  const [log, setLog] = useState<string>('')

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!file) return

    const form = new FormData()
    form.append('arquivo', file)
    const res = await fetch('/v1/etl/epi/upload', { method: 'POST', body: form })
    const json = await res.json()
    setLog(JSON.stringify(json, null, 2))
  }

  return (
    <form onSubmit={onSubmit} className="rounded-2xl border bg-white p-4 space-y-3">
      <div className="font-medium">Upload de Indicadores (CSV/Planilha)</div>
      <input type="file" accept=".csv, application/vnd.ms-excel, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
             onChange={e => setFile(e.target.files?.[0] || null)} />
      <button className="px-4 py-2 rounded bg-sky-600 text-white hover:bg-sky-700">Enviar</button>
      {log && <pre className="text-xs bg-slate-50 p-2 rounded max-h-48 overflow-auto">{log}</pre>}
    </form>
  )
}
