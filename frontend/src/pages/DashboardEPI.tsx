import React, { useState, useEffect, useMemo } from 'react';
import KPICards from '../components/dashboard/KPICards';
import TimeSeriesChart from '../components/dashboard/TimeSeriesChart';
import TopNChart from '../components/dashboard/TopNChart';
import { useFilters, FilterDrawer } from '@/design-system/filters';
import { dashboardFilterConfig } from '@/modules/dashboard/filters/config';
import { Filter as FilterIcon } from 'lucide-react';
import { dashboardEstatisticasParams, dashboardTopNParams } from '@/modules/dashboard/filters/adapter';

// Tipos mínimos para remover 'any' e alinhar com componentes filhos
type KPIVariacao = {
  valor_atual: number;
  valor_anterior: number;
  variacao_absoluta: number;
  variacao_percentual: number;
  tendencia: 'alta' | 'baixa' | 'estavel';
};

type KPICard = {
  titulo: string;
  valor: number;
  unidade: string;
  variacao?: KPIVariacao;
  icone?: string;
  cor?: string;
  descricao?: string;
};

type KpisData = {
  total_casos: KPICard;
  total_obitos: KPICard;
  taxa_letalidade: KPICard;
  incidencia_media: KPICard;
  municipios_risco_alto?: KPICard;
  casos_graves?: KPICard;
  ultima_atualizacao?: string;
  periodo_inicio?: string;
  periodo_fim?: string;
};

type TimeSeriesPoint = { data: string; valor: number };
type TimeSeriesSerie = { nome: string; tipo: string; unidade: string; dados: TimeSeriesPoint[]; cor?: string };
type TimeSeriesData = {
  series: TimeSeriesSerie[];
  periodo_agregacao: string;
  periodo_inicio: string;
  periodo_fim: string;
  total_pontos: number;
};

type SerieAPIPoint = { data: string; valor: number };
type HeatmapPoint = { lat: number; lng: number; intensity: number };

type TopNEntry = { posicao: number; codigo_ibge: string; nome: string; valor: number; valor_secundario?: number; percentual?: number; nivel_risco?: string; cor_hex?: string };
type TopNData = {
  ranking: TopNEntry[];
  tipo_indicador: string;
  unidade: string;
  total_items: number;
  limite: number;
  periodo_inicio: string;
  periodo_fim: string;
  agregacao?: string;
};

const DashboardEPI: React.FC = () => {
  const { filters: dsFilters, setFilter, reset } = useFilters({ config: dashboardFilterConfig })
  const [openFilters, setOpenFilters] = useState(false)

  const computed = useMemo(() => {
    const getNum = (v: unknown) => (v == null || v === '' ? undefined : Number(v))
    const ano = getNum(dsFilters['ano']) ?? new Date().getFullYear()
    const semanaInicio = getNum(dsFilters['semanaInicio'])
    const semanaFim = getNum(dsFilters['semanaFim'])
    const doencaTipo = (dsFilters['doencaTipo'] as string) || undefined
    return { ano, semanaInicio, semanaFim, doencaTipo }
  }, [dsFilters])
  
  const [kpis, setKpis] = useState<KpisData | null>(null);
  const [series, setSeries] = useState<TimeSeriesData | null>(null);
  const [topN, setTopN] = useState<TopNData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch KPIs usando API Mapa
  useEffect(() => {
    const fetchKPIs = async () => {
      try {
        setLoading(true);
        const params = dashboardEstatisticasParams({
          ano: computed.ano,
          semanaInicio: computed.semanaInicio,
          semanaFim: computed.semanaFim,
        })
        
        const response = await fetch(`/api/mapa/estatisticas?${params}`);
        if (!response.ok) throw new Error('Erro ao carregar estatísticas');
        
        const stats = await response.json();
        
        // Transformar para formato KPIs
        const kpisData: KpisData = {
          total_casos: {
            titulo: 'Total de Casos',
            valor: stats.total_casos || 0,
            unidade: 'casos',
            icone: 'Activity',
            cor: '#2196F3',
            descricao: `${stats.total_municipios || 0} municípios afetados`,
          },
          total_obitos: {
            titulo: 'Total de Óbitos',
            valor: stats.total_obitos || 0,
            unidade: 'óbitos',
            icone: 'AlertCircle',
            cor: '#F44336',
          },
          taxa_letalidade: {
            titulo: 'Taxa de Letalidade',
            valor: stats.taxa_letalidade || 0,
            unidade: '%',
            icone: 'AlertTriangle',
            cor: '#FF9800',
          },
          incidencia_media: {
            titulo: 'Incidência Média',
            valor: stats.incidencia_media || 0,
            unidade: '/100k hab',
            icone: 'TrendingUp',
            cor: '#FFC107',
            descricao: `Máxima: ${(stats.incidencia_maxima || 0).toFixed(2)}/100k`,
          },
          municipios_risco_alto: {
            titulo: 'Municípios Alto Risco',
            valor: (stats.distribuicao_risco?.MUITO_ALTO || 0) + (stats.distribuicao_risco?.ALTO || 0),
            unidade: 'municípios',
            icone: 'Users',
            cor: '#F44336',
          },
          periodo_inicio: stats.periodo_inicio,
          periodo_fim: stats.periodo_fim,
        };
        
        setKpis(kpisData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Erro desconhecido');
      } finally {
        setLoading(false);
      }
    };

    fetchKPIs();
  }, [computed]);

  // Fetch Series Temporais - Cuiabá (capital como exemplo)
  useEffect(() => {
    const fetchSeries = async () => {
      try {
        const codigoCuiaba = '5103403';
        const response = await fetch(
          `/api/mapa/series-temporais/${codigoCuiaba}?ano=${computed.ano}`
        );
        if (!response.ok) throw new Error('Erro ao carregar séries');
        
        const serieData = await response.json();
        
        // Transformar para formato esperado
        const timeSeriesData: TimeSeriesData = {
          series: [
            {
              nome: serieData.nome || 'Cuiabá',
              tipo: 'incidencia',
              unidade: '/100k hab',
              dados: serieData.serie.map((s: SerieAPIPoint) => ({
                data: s.data,
                valor: s.valor,
              })),
              cor: '#2196F3',
            },
          ],
          periodo_agregacao: 'semanal',
          periodo_inicio: computed.ano + '-01-01',
          periodo_fim: computed.ano + '-12-31',
          total_pontos: serieData.serie.length,
        };
        
        setSeries(timeSeriesData);
      } catch (err) {
        console.error('Erro ao carregar séries:', err);
      }
    };

    fetchSeries();
  }, [computed]);

  // Fetch Top N - Usando estatísticas e heatmap para ranking
  useEffect(() => {
    const fetchTopN = async () => {
      try {
        const params = dashboardTopNParams({
          ano: computed.ano,
          semanaInicio: computed.semanaInicio,
          semanaFim: computed.semanaFim,
        })
        
        const response = await fetch(
          `/api/mapa/heatmap?${params}`
        );
        if (!response.ok) throw new Error('Erro ao carregar ranking');
        
        const heatmapData = await response.json();
        
        // Pegar top 10 por intensidade e criar ranking fictício
        const sortedPoints = [...(heatmapData.points as HeatmapPoint[])]
          .sort((a: HeatmapPoint, b: HeatmapPoint) => b.intensity - a.intensity)
          .slice(0, 10);
        
        const topNData: TopNData = {
          ranking: sortedPoints.map((p: HeatmapPoint, idx: number) => ({
            posicao: idx + 1,
            codigo_ibge: '510' + (1000 + idx), // Fictício
            nome: `Município ${idx + 1}`,
            valor: p.intensity,
            nivel_risco: p.intensity > 500 ? 'MUITO_ALTO' : p.intensity > 300 ? 'ALTO' : 'MEDIO',
            cor_hex: p.intensity > 500 ? '#F44336' : p.intensity > 300 ? '#FF9800' : '#FFC107',
          })),
          tipo_indicador: 'incidencia',
          unidade: '/100k hab',
          total_items: sortedPoints.length,
          limite: 10,
          periodo_inicio: computed.ano + '-01-01',
          periodo_fim: computed.ano + '-12-31',
        };
        
        setTopN(topNData);
      } catch (err) {
        console.error('Erro ao carregar ranking:', err);
      }
    };

    fetchTopN();
  }, [computed]);

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

      {/* Filtros (Design System) */}
      <div className="mb-4 flex justify-end">
        <button
          onClick={() => setOpenFilters(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 flex items-center space-x-2"
        >
          <FilterIcon className="w-4 h-4" />
          <span>Filtros</span>
        </button>
      </div>
      <FilterDrawer
        open={openFilters}
        onClose={() => setOpenFilters(false)}
        config={dashboardFilterConfig}
        values={dsFilters}
        onChange={(field, value) => setFilter(field, value)}
        onReset={() => reset()}
      />

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
