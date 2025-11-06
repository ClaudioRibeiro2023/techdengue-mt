import React from 'react';
import { Activity, AlertTriangle, TrendingUp, Users, AlertCircle, Heart, TrendingDown, Minus, type LucideIcon } from 'lucide-react';

interface KPIVariacao {
  valor_atual: number;
  valor_anterior: number;
  variacao_absoluta: number;
  variacao_percentual: number;
  tendencia: 'alta' | 'baixa' | 'estavel';
}

interface KPICard {
  titulo: string;
  valor: number;
  unidade: string;
  variacao?: KPIVariacao;
  icone?: string;
  cor?: string;
  descricao?: string;
}

interface KPICardsProps {
  data: {
    total_casos: KPICard;
    total_obitos: KPICard;
    taxa_letalidade: KPICard;
    incidencia_media: KPICard;
    municipios_risco_alto?: KPICard;
    casos_graves?: KPICard;
  };
}

const iconMap: Record<string, LucideIcon> = {
  Activity,
  AlertTriangle,
  TrendingUp,
  Users,
  AlertCircle,
  Heart,
};

// Mapa de classes Tailwind para cores conhecidas
const COLOR_CLASSES: Record<string, { border: string; bg: string; text: string }> = {
  '#2196F3': { border: 'border-blue-500', bg: 'bg-blue-500', text: 'text-blue-500' },
  '#4CAF50': { border: 'border-green-500', bg: 'bg-green-500', text: 'text-green-500' },
  '#FFC107': { border: 'border-amber-500', bg: 'bg-amber-500', text: 'text-amber-500' },
  '#FF9800': { border: 'border-orange-500', bg: 'bg-orange-500', text: 'text-orange-500' },
  '#F44336': { border: 'border-red-500', bg: 'bg-red-500', text: 'text-red-500' },
};

const KPICards: React.FC<KPICardsProps> = ({ data }) => {
  const renderCard = (card: KPICard) => {
    const Icon = card.icone && iconMap[card.icone] ? iconMap[card.icone] : Activity;
    const defaultColor = '#2196F3';
    const colorKey = (card.cor && COLOR_CLASSES[card.cor]) ? card.cor : defaultColor;
    const colors = COLOR_CLASSES[colorKey];
    
    return (
      <div
        key={card.titulo}
        className={`bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow border-t-4 ${colors.border}`}
      >
        {/* Header com ícone */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h3 className="text-sm font-medium text-gray-600 mb-1">{card.titulo}</h3>
            <p className="text-3xl font-bold text-gray-900">
              {card.valor.toLocaleString('pt-BR', { maximumFractionDigits: 2 })}
              <span className="text-lg font-normal text-gray-500 ml-2">{card.unidade}</span>
            </p>
          </div>
          <div className={`p-3 rounded-lg ${colors.bg} bg-opacity-20`}>
            <Icon className={`w-6 h-6 ${colors.text}`} />
          </div>
        </div>

        {/* Variação */}
        {card.variacao && (
          <div className="flex items-center space-x-2">
            {card.variacao.tendencia === 'alta' && (
              <>
                <TrendingUp className="w-4 h-4 text-red-500" />
                <span className="text-sm font-medium text-red-500">
                  +{card.variacao.variacao_percentual.toFixed(1)}%
                </span>
              </>
            )}
            {card.variacao.tendencia === 'baixa' && (
              <>
                <TrendingDown className="w-4 h-4 text-green-500" />
                <span className="text-sm font-medium text-green-500">
                  {card.variacao.variacao_percentual.toFixed(1)}%
                </span>
              </>
            )}
            {card.variacao.tendencia === 'estavel' && (
              <>
                <Minus className="w-4 h-4 text-gray-500" />
                <span className="text-sm font-medium text-gray-500">
                  {card.variacao.variacao_percentual.toFixed(1)}%
                </span>
              </>
            )}
            <span className="text-sm text-gray-500">vs período anterior</span>
          </div>
        )}

        {/* Descrição */}
        {card.descricao && (
          <p className="text-xs text-gray-500 mt-2">{card.descricao}</p>
        )}
      </div>
    );
  };

  const cards = [
    data.total_casos,
    data.total_obitos,
    data.taxa_letalidade,
    data.incidencia_media,
    ...(data.municipios_risco_alto ? [data.municipios_risco_alto] : []),
    ...(data.casos_graves ? [data.casos_graves] : []),
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card) => renderCard(card))}
    </div>
  );
};

export default KPICards;
