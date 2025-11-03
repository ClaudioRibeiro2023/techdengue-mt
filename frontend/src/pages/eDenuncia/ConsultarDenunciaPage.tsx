import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import type { DenunciaResponse } from '@/types/denuncia'

export default function ConsultarDenunciaPage() {
  const { protocolo } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState<DenunciaResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let mounted = true
    async function run() {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(`/api/denuncias/${protocolo}`)
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          throw new Error(err.detail || 'Não foi possível consultar a denúncia')
        }
        const json = await res.json()
        if (mounted) setData(json)
      } catch (e: any) {
        if (mounted) setError(e?.message || 'Erro ao consultar')
      } finally {
        if (mounted) setLoading(false)
      }
    }
    if (protocolo) run()
    return () => { mounted = false }
  }, [protocolo])

  const statusColor = (s?: string) => {
    switch (s) {
      case 'PENDENTE': return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'EM_ANALISE': return 'bg-blue-100 text-blue-800 border-blue-200'
      case 'ATIVIDADE_CRIADA': return 'bg-green-100 text-green-800 border-green-200'
      case 'DESCARTADA': return 'bg-red-100 text-red-800 border-red-200'
      default: return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-gray-700">Carregando...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-lg text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-3">Consulta de Denúncia</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <div className="space-y-3">
            <button
              onClick={() => navigate('/denuncia')}
              className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Fazer Nova Denúncia
            </button>
            <button
              onClick={() => navigate('/')}
              className="w-full px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Voltar para Home
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-lg shadow-lg p-8 max-w-2xl w-full">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Consulta de Denúncia</h2>

        <div className="grid gap-4">
          <div className="bg-blue-50 border-2 border-blue-200 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Número do Protocolo</p>
            <div className="flex items-center justify-between gap-3">
              <p className="text-2xl font-mono font-bold text-blue-600 select-all">{data?.numero_protocolo}</p>
              <button
                onClick={async () => { if (data?.numero_protocolo) await navigator.clipboard.writeText(data.numero_protocolo) }}
                className="px-3 py-2 border-2 border-gray-300 rounded-lg text-gray-700 text-sm hover:bg-gray-50"
              >
                Copiar
              </button>
            </div>
          </div>

          <div className={`border rounded-lg p-4 ${statusColor(data?.status)}`}>
            <div className="text-sm">Status atual</div>
            <div className="font-semibold text-lg">{data?.status}</div>
          </div>

          <div className="border rounded-lg p-4">
            <div className="text-sm text-gray-600">Endereço</div>
            <div className="font-medium">{data?.endereco}</div>
            <div className="text-sm text-gray-600 mt-1">Bairro</div>
            <div className="font-medium">{data?.bairro}</div>
            <div className="text-sm text-gray-600 mt-1">Município</div>
            <div className="font-medium">{data?.municipio_nome} ({data?.municipio_codigo})</div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="border rounded-lg p-3">
              <div className="text-xs text-gray-500">Prioridade</div>
              <div className="font-semibold">{data?.chatbot_classificacao}</div>
            </div>
            <div className="border rounded-lg p-3">
              <div className="text-xs text-gray-500">Criado em</div>
              <div className="font-semibold">{data?.criado_em ? new Date(data.criado_em).toLocaleString() : '-'}</div>
            </div>
            <div className="border rounded-lg p-3">
              <div className="text-xs text-gray-500">Atualizado em</div>
              <div className="font-semibold">{data?.atualizado_em ? new Date(data.atualizado_em).toLocaleString() : '-'}</div>
            </div>
          </div>

          {data?.atividade_id && (
            <div className="border rounded-lg p-4">
              <div className="text-sm text-gray-600">Atividade relacionada</div>
              <div className="font-mono text-sm">{data.atividade_id}</div>
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <button
              onClick={() => navigate('/denuncia')}
              className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
            >
              Fazer Nova Denúncia
            </button>
            <button
              onClick={() => navigate('/')}
              className="flex-1 px-6 py-3 border-2 border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50 transition-colors"
            >
              Voltar para Home
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
