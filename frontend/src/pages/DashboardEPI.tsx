import React, { useState, useEffect } from 'react';
import KPICards from '../components/dashboard/KPICards';
import TimeSeriesChart from '../components/dashboard/TimeSeriesChart';
import TopNChart from '../components/dashboard/TopNChart';

interface DashboardFilters {
  ano: number;
  semanaInicio?: number;
  semanaFim?: number;
  doencaTipo?: string;
}

const DashboardEPI: React.FC = () => {
  const [filters, setFilters] = useState<DashboardFilters>({
    ano: new Date().getFullYear(),
  });
  
  const [kpis, setKpis] = useState<any>(null);
  const [series, setSeries] = useState<any>(null);
  const [topN, setTopN] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch KPIs
  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        setLoading(true);
        const params = new URLSearchParams({
          ano: filters.ano.toString(),
          ...(filters.semanaInicio && { semana_epi_inicio: filters.semanaInicio.toString() }),
          ...(filters.semanaFim && { semana_epi_fim: filters.semanaFim.toString() }),
          ...(filters.doencaTipo && { doenca_tipo: filters.doencaTipo }),
        });
        
        const response = await fetch(`/api/indicadores/kpis?${params}`);
        if (!response.ok) throw new Error('Erro ao carregar KPIs');
        
        const data = await response.json();
        setKpis(data);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
  }, [filters]);

  // Fetch Series Temporais
  useEffect(() => {
    const fetchSeries = async () => {
      try {
        const params = new URLSearchParams({
          ano: filters.ano.toString(),
          periodo_agregacao: 'semanal',
          ...(filters.doencaTipo && { doenca_tipo: filters.doencaTipo }),
        });
        
        const response = await fetch(`/api/indicadores/series-temporais?${params}`);
        if (!response.ok) throw new Error('Erro ao carregar séries');
        
        const data = await response.json();
        setSeries(data);
      } catch (err) {
        console.error('Erro ao carregar séries:', err);
      }
    };

    fetchSeries();
  }, [filters]);

  // Fetch Top N
  useEffect(() => {
    const fetchTopN = async () => {
      try {
        const params = new URLSearchParams({
          ano: filters.ano.toString(),
          limite: '10',
          tipo_indicador: 'casos',
          ...(filters.semanaInicio && { semana_epi_inicio: filters.semanaInicio.toString() }),
          ...(filters.semanaFim && { semana_epi_fim: filters.semanaFim.toString() }),
          ...(filters.doencaTipo && { doenca_tipo: filters.doencaTipo }),
        });
        
        const response = await fetch(`/api/indicadores/top?${params}`);
        if (!response.ok) throw new Error('Erro ao carregar ranking');
        
        const data = await response.json();
        setTopN(data);
      } catch (err) {
        console.error('Erro ao carregar ranking:', err);
      }
    };

    fetchTopN();
  }, [filters]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Dashboard Epidemiológico
        </h1>
        <p className="text-gray-600">
          Indicadores e métricas de vigilância epidemiológica - MT
        </p>
      </div>

      {/* Filtros */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ano
            </label>
            <select
              value={filters.ano}
              onChange={(e) => setFilters({ ...filters, ano: parseInt(e.target.value) })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="2024">2024</option>
              <option value="2023">2023</option>
              <option value="2022">2022</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Semana Início
            </label>
            <input
              type="number"
              min="1"
              max="53"
              placeholder="1-53"
              value={filters.semanaInicio || ''}
              onChange={(e) => setFilters({ ...filters, semanaInicio: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Semana Fim
            </label>
            <input
              type="number"
              min="1"
              max="53"
              placeholder="1-53"
              value={filters.semanaFim || ''}
              onChange={(e) => setFilters({ ...filters, semanaFim: e.target.value ? parseInt(e.target.value) : undefined })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Doença
            </label>
            <select
              value={filters.doencaTipo || ''}
              onChange={(e) => setFilters({ ...filters, doencaTipo: e.target.value || undefined })}
              className="w-full border border-gray-300 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Todas</option>
              <option value="DENGUE">Dengue</option>
              <option value="ZIKA">Zika</option>
              <option value="CHIKUNGUNYA">Chikungunya</option>
              <option value="FEBRE_AMARELA">Febre Amarela</option>
            </select>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      {kpis && <KPICards data={kpis} />}

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        {/* Série Temporal */}
        {series && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Evolução Temporal</h2>
            <TimeSeriesChart data={series} />
          </div>
        )}

        {/* Top N */}
        {topN && (
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Top 10 Municípios</h2>
            <TopNChart data={topN} />
          </div>
        )}
      </div>

      {/* Footer info */}
      <div className="mt-8 text-center text-sm text-gray-500">
        <p>Última atualização: {kpis?.ultima_atualizacao && new Date(kpis.ultima_atualizacao).toLocaleString('pt-BR')}</p>
        <p className="mt-1">Período: {kpis?.periodo_inicio} a {kpis?.periodo_fim}</p>
      </div>
    </div>
  );
};

export default DashboardEPI;
