import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

interface ItemRanking {
  posicao: number;
  codigo_ibge: string;
  nome: string;
  valor: number;
  valor_secundario?: number;
  percentual?: number;
  nivel_risco?: string;
  cor_hex?: string;
}

interface TopNChartProps {
  data: {
    ranking: ItemRanking[];
    tipo_indicador: string;
    unidade: string;
    total_items: number;
    limite: number;
    periodo_inicio: string;
    periodo_fim: string;
    agregacao?: string;
  };
}

const nivelRiscoColors: Record<string, string> = {
  BAIXO: '#4CAF50',
  MEDIO: '#FFC107',
  ALTO: '#FF9800',
  MUITO_ALTO: '#F44336',
};

const TopNChart: React.FC<TopNChartProps> = ({ data }) => {
  if (!data || !data.ranking || data.ranking.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Nenhum dado de ranking disponível
      </div>
    );
  }

  // Preparar dados para o gráfico de barras
  const labels = data.ranking.map((item) => item.nome);
  const valores = data.ranking.map((item) => item.valor);
  const cores = data.ranking.map((item) => 
    item.cor_hex || (item.nivel_risco ? nivelRiscoColors[item.nivel_risco] : '#2196F3')
  );

  const chartData = {
    labels,
    datasets: [
      {
        label: `${data.tipo_indicador} (${data.unidade})`,
        data: valores,
        backgroundColor: cores,
        borderColor: cores,
        borderWidth: 1,
      },
    ],
  };

  const options: ChartOptions<'bar'> = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const item = data.ranking[context.dataIndex];
            const lines = [
              `${data.tipo_indicador}: ${context.parsed.x.toLocaleString('pt-BR', { maximumFractionDigits: 2 })} ${data.unidade}`,
            ];
            
            if (item.percentual) {
              lines.push(`% do total: ${item.percentual.toFixed(2)}%`);
            }
            
            if (item.nivel_risco) {
              lines.push(`Risco: ${item.nivel_risco.replace('_', ' ')}`);
            }
            
            return lines;
          }
        }
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          callback: function(value) {
            return value.toLocaleString('pt-BR');
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      y: {
        grid: {
          display: false,
        },
      },
    },
  };

  return (
    <div>
      <div className="h-96 mb-4">
        <Bar data={chartData} options={options} />
      </div>

      {/* Lista textual */}
      <div className="space-y-2">
        {data.ranking.slice(0, 5).map((item) => (
          <div
            key={item.codigo_ibge}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <div className="flex-shrink-0 w-6 h-6 bg-gray-300 rounded-full flex items-center justify-center text-xs font-bold">
                {item.posicao}
              </div>
              <div>
                <p className="font-medium text-gray-900">{item.nome}</p>
                <p className="text-xs text-gray-500">
                  Código IBGE: {item.codigo_ibge}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-bold text-gray-900">
                {item.valor.toLocaleString('pt-BR', { maximumFractionDigits: 2 })}
              </p>
              <p className="text-xs text-gray-500">{data.unidade}</p>
              {item.percentual && (
                <p className="text-xs text-gray-500">
                  {item.percentual.toFixed(1)}% do total
                </p>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 text-sm text-gray-500 text-center">
        Exibindo top {data.limite} de {data.total_items} municípios
      </div>
    </div>
  );
};

export default TopNChart;
