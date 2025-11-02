import React, { useState } from 'react'
import { api, linkRelatorio } from '../lib/api'

export const Relatorios: React.FC = () => {
  const [municipio, setMunicipio] = useState('3106200')
  const [competencia, setCompetencia] = useState('2025-09-30')
  const [links, setLinks] = useState<{pdf?: string, csv?: string}>({})

  async function gerarEPI01() {
    const q = new URLSearchParams({ municipio_cod_ibge: municipio, competencia, formato: 'pdf' })
    const data = await api<{ pdf_url: string, csv_url?: string }>('/relatorios/epi01?' + q.toString())
    setLinks(linkRelatorio(data))
  }

  return (
    <div className="space-y-4">
      <div className="rounded-2xl border bg-white p-4 space-y-3">
        <div className="font-medium">Relatório EPI01</div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <input className="border rounded px-2 py-1" placeholder="Município (IBGE)" value={municipio} onChange={e=>setMunicipio(e.target.value)} />
          <input className="border rounded px-2 py-1" type="date" value={competencia} onChange={e=>setCompetencia(e.target.value)} />
          <button onClick={gerarEPI01} className="px-4 py-2 rounded bg-sky-600 text-white hover:bg-sky-700">Gerar</button>
        </div>
        {links.pdf && <div className="text-sm space-x-4">
          <a href={links.pdf} className="underline">Baixar PDF</a>
          {links.csv && <a href={links.csv} className="underline">Baixar CSV</a>}
        </div>}
      </div>
    </div>
  )
}
