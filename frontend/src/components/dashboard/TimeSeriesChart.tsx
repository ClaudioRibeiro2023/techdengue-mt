import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ChartOptions
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

interface PontoSerie {
  data: string;
  valor: number;
}

interface SerieTemporal {
  nome: string;
  tipo: string;
  unidade: string;
  dados: PontoSerie[];
  cor?: string;
}

interface TimeSeriesChartProps {
  data: {
    series: SerieTemporal[];
    periodo_agregacao: string;
    periodo_inicio: string;
    periodo_fim: string;
    total_pontos: number;
  };
}

const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ data }) => {
  if (!data || !data.series || data.series.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-500">
        Nenhuma série temporal disponível
      </div>
    );
  }

  // Preparar datasets
  const datasets = data.series.map((serie) => ({
    label: serie.nome,
    data: serie.dados.map((ponto) => ponto.valor),
    borderColor: serie.cor || '#2196F3',
    backgroundColor: `${serie.cor || '#2196F3'}33`,
    tension: 0.3,
    borderWidth: 2,
    pointRadius: 3,
    pointHoverRadius: 5,
  }));

  // Labels (datas)
  const labels = data.series[0]?.dados.map((ponto) => ponto.data) || [];

  const chartData = {
    labels,
    datasets,
  };

  const options: ChartOptions<'line'> = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top' as const,
        labels: {
          usePointStyle: true,
          padding: 15,
        },
      },
      tooltip: {
        mode: 'index' as const,
        intersect: false,
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
              label += ': ';
            }
            if (context.parsed.y !== null) {
              label += context.parsed.y.toLocaleString('pt-BR', { maximumFractionDigits: 2 });
            }
            return label;
          }
        }
      },
    },
    scales: {
      y: {
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
      x: {
        grid: {
          display: false,
        },
        ticks: {
          maxRotation: 45,
          minRotation: 45,
        },
      },
    },
    interaction: {
      mode: 'nearest' as const,
      axis: 'x' as const,
      intersect: false,
    },
  };

  return (
    <div className="h-80">
      <Line data={chartData} options={options} />
      <div className="mt-4 text-sm text-gray-500 text-center">
        Período: {data.periodo_inicio} a {data.periodo_fim} | Agregação: {data.periodo_agregacao}
      </div>
    </div>
  );
};

export default TimeSeriesChart;
