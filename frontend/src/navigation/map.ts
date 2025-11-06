import type { NavigationMap } from './types'
import type { UserRole } from '@/config/auth'

export const NAVIGATION: NavigationMap = {
  modules: [
    // WEB MAPAS
    {
      id: 'mapa-vivo',
      name: 'Mapa Vivo',
      description: 'WebMapa Unificado - Navegação e análises espaciais',
      path: '/mapa',
      topNav: true,
      icon: 'Map',
      group: 'Web Mapas',
      functions: [
        { id: 'mapa-principal', name: 'Mapa Principal', subtitle: 'Navegação, busca e filtros', path: '/mapa', category: 'MAPEAMENTO', icon: 'Map' },
        { id: 'mapa-calor', name: 'Mapa de Calor', subtitle: 'Densidade e intensidade', path: '/mapa?view=heatmap', category: 'ANALISE', icon: 'Flame' },
        { id: 'clusters', name: 'Clusters', subtitle: 'Agrupamentos espaciais', path: '/mapa?view=clusters', category: 'ANALISE', icon: 'Grid3X3' },
        { id: 'hotspots-mapa', name: 'Hotspots', subtitle: 'Detecção espaço-temporal', path: '/mapa?view=hotspots', category: 'ANALISE', icon: 'MapPin' },
        { id: 'zonas-risco', name: 'Zonas de Risco', subtitle: 'Delimitação e desenho', path: '/mapa?view=risk', category: 'ANALISE', icon: 'AlertTriangle' },
        { id: 'pontos-criticos', name: 'Pontos Críticos', subtitle: 'Alvos e prioridade', path: '/mapa?view=critical', category: 'ANALISE', icon: 'AlertOctagon' },
        { id: 'camadas-externas', name: 'Camadas Externas', subtitle: 'IBGE, saneamento, saúde', path: '/mapa?view=layers', category: 'MAPEAMENTO', icon: 'Layers' },
      ],
    },

    // PAINÉIS
    {
      id: 'dashboard-executivo',
      name: 'Panorama Executivo',
      description: 'Dashboard consolidado e KPIs estratégicos',
      path: '/dashboard',
      topNav: true,
      icon: 'LayoutDashboard',
      group: 'Dados',
      functions: [
        { id: 'dashboard-consolidado', name: 'Dashboard Consolidado', subtitle: 'KPIs e visão geral', path: '/dashboard', category: 'INDICADORES', icon: 'LayoutGrid' },
        { id: 'rankings', name: 'Rankings', subtitle: 'Metas e semáforos', path: '/dashboard?view=rankings', category: 'INDICADORES', icon: 'TrendingUp' },
        { id: 'alertas', name: 'Alertas', subtitle: 'Notificações e watchlist', path: '/dashboard?view=alerts', category: 'CONTROLE', icon: 'Bell' },
        { id: 'relatorios-rapidos', name: 'Relatórios Rápidos', subtitle: 'Snapshots e exportes', path: '/dashboard?view=reports', category: 'INDICADORES', icon: 'FileText' },
      ],
    },

    {
      id: 'relatorios',
      name: 'Relatórios & Indicadores',
      description: 'Relatórios EPI e exportações',
      path: '/relatorios',
      topNav: true,
      icon: 'BarChart3',
      group: 'Dados',
      functions: [
        { id: 'relatorios-epi', name: 'Relatórios EPI', path: '/relatorios?type=epi', category: 'INDICADORES', icon: 'FileSpreadsheet' },
        { id: 'exportacoes', name: 'Exportações', path: '/relatorios?view=export', category: 'OPERACIONAL', icon: 'Download' },
        { id: 'cadernos-analiticos', name: 'Cadernos Analíticos', path: '/relatorios?view=notebooks', category: 'ANALISE', icon: 'BookOpen' },
      ],
    },

    {
      id: 'etl-integracao',
      name: 'ETL & Integração',
      description: 'Importadores e tratamento de dados',
      path: '/etl',
      topNav: true,
      icon: 'Database',
      badge: 'BETA',
      group: 'Serviços Técnicos',
      roles: ['ADMIN'] as UserRole[],
      functions: [
        { id: 'import-sinan', name: 'Importadores SINAN', path: '/etl?src=sinan', category: 'OPERACIONAL', icon: 'Upload' },
        { id: 'import-liraa', name: 'Importadores LIRAa', path: '/etl?src=liraa', category: 'OPERACIONAL', icon: 'Upload' },
        { id: 'import-ovitrampas', name: 'Importadores Ovitrampas', path: '/etl?src=ovitrampas', category: 'OPERACIONAL', icon: 'Upload' },
        { id: 'import-ibge', name: 'Importadores IBGE/Shape', path: '/etl?src=ibge', category: 'OPERACIONAL', icon: 'Upload' },
        { id: 'tratamento', name: 'Tratamento/Mapeamento', path: '/etl?view=transform', category: 'OPERACIONAL', icon: 'Workflow' },
        { id: 'catalogo-dados', name: 'Catálogo de Dados', path: '/etl?view=catalog', category: 'CONTROLE', icon: 'BookMarked' },
        { id: 'qualidade-rastros', name: 'Qualidade & Rastros', path: '/etl?view=quality', category: 'CONTROLE', icon: 'Shield' },
        { id: 'logs-reprocesso', name: 'Logs & Reprocesso', path: '/etl?view=reprocess', category: 'CONTROLE', icon: 'History' },
      ],
    },

    {
      id: 'previsao-simulacao',
      name: 'Previsão & Simulação',
      description: 'Nowcasting, Rt e cenários epidemiológicos',
      path: '/modulos/previsao-simulacao',
      icon: 'Brain',
      badge: 'IA',
      group: 'Dados',
      roles: ['GESTOR', 'VIGILANCIA', 'ADMIN'] as UserRole[],
      functions: [
        { id: 'nowcasting-rt', name: 'Nowcasting / Rt', subtitle: 'Atraso de notificação e transmissibilidade', path: '/modulos/previsao-simulacao?view=nowcasting', category: 'ANALISE', icon: 'Zap' },
        { id: 'previsao-2-4sem', name: 'Previsão 2–4 semanas', subtitle: 'Casos/risco por município', path: '/modulos/previsao-simulacao?view=forecast', category: 'ANALISE', icon: 'TrendingUp' },
        { id: 'cenarios-intervencao', name: 'Cenários de Intervenção', subtitle: 'Simulação de impacto', path: '/modulos/previsao-simulacao?view=scenarios', category: 'ANALISE', icon: 'GitBranch' },
        { id: 'risco-climatico', name: 'Risco Climático', subtitle: 'Camadas ambientais (chuva/temperatura)', path: '/modulos/previsao-simulacao?view=climate', category: 'ANALISE', icon: 'Cloud' },
      ],
    },
    // VIGILÂNCIA
    {
      id: 'vigilancia-entomologica',
      name: 'Vigilância Entomológica',
      description: 'Monitoramento de populações vetoriais e índices',
      path: '/modulos/vigilancia-entomologica',
      icon: 'Bug',
      group: 'Vigilância',
      roles: ['VIGILANCIA', 'GESTOR'] as UserRole[],
      functions: [
        { id: 'entomo-visao-geral', name: 'Visão Geral', subtitle: 'Panorama de infestação e tendência', path: '/modulos/vigilancia-entomologica?view=overview', category: 'ANALISE', icon: 'Eye' },
        { id: 'analise-sazonal', name: 'Análise Sazonal', subtitle: 'Séries temporais por município/bairro', path: '/modulos/vigilancia-entomologica?view=sazonal', category: 'ANALISE', icon: 'Calendar' },
        { id: 'ovitrampas', name: 'Ovitrampas', subtitle: 'Distribuição espacial, reposição e produtividade', path: '/modulos/vigilancia-entomologica?view=ovitrampas', category: 'MAPEAMENTO', icon: 'MapPinned' },
        { id: 'indices-entomo', name: 'Índices (IPO/IDO/IMO)', subtitle: 'Cálculo, metas e ranking', path: '/modulos/vigilancia-entomologica?view=indices', category: 'INDICADORES', icon: 'TrendingUp' },
        { id: 'qualidade-entomo', name: 'Qualidade', subtitle: 'Completude, consistência e outliers', path: '/modulos/vigilancia-entomologica?view=qualidade', category: 'CONTROLE', icon: 'CheckCircle' },
        // Funções de mapa dentro do módulo (conforme bench)
        { id: 'entomo-mapa-principal', name: 'Mapa Principal', subtitle: 'Navegação e filtros', path: '/modulos/vigilancia-entomologica?view=mapa', category: 'MAPEAMENTO', icon: 'Map' },
        { id: 'entomo-mapa-calor', name: 'Mapa de Calor', subtitle: 'Intensidade e densidade', path: '/modulos/vigilancia-entomologica?view=heatmap', category: 'ANALISE', icon: 'Flame' },
        { id: 'entomo-hotspots', name: 'Hotspots', subtitle: 'Detecção espaço-temporal', path: '/modulos/vigilancia-entomologica?view=hotspots', category: 'ANALISE', icon: 'MapPin' },
        { id: 'entomo-zonas-risco', name: 'Zonas de Risco', subtitle: 'Delimitação e desenho', path: '/modulos/vigilancia-entomologica?view=risk', category: 'ANALISE', icon: 'AlertTriangle' },
        { id: 'entomo-camadas', name: 'Camadas (clusters, pontos)', subtitle: 'Camadas e agrupamentos', path: '/modulos/vigilancia-entomologica?view=camadas', category: 'MAPEAMENTO', icon: 'Layers' },
      ],
    },

    {
      id: 'vigilancia-epidemiologica',
      name: 'Vigilância Epidemiológica',
      description: 'Casos, incidência e hotspots epidemiológicos',
      path: '/modulos/vigilancia-epidemiologica',
      icon: 'Activity',
      group: 'Vigilância',
      roles: ['VIGILANCIA', 'GESTOR'] as UserRole[],
      functions: [
        { id: 'epi-visao-geral', name: 'Visão Geral', subtitle: 'Incidência, letalidade, Rt/nowcasting', path: '/modulos/vigilancia-epidemiologica?view=overview', category: 'ANALISE', icon: 'Eye' },
        { id: 'epi-nowcasting', name: 'Nowcasting / Rt', subtitle: 'Transmissibilidade e atraso', path: '/modulos/vigilancia-epidemiologica?view=nowcasting', category: 'ANALISE', icon: 'Activity' },
        { id: 'series-temporais', name: 'Séries Temporais', subtitle: 'Casos por semana/município', path: '/modulos/vigilancia-epidemiologica?view=temporal', category: 'ANALISE', icon: 'LineChart' },
        { id: 'mapa-incidencia', name: 'Mapa de Incidência', subtitle: 'Choropleth e pontos de casos', path: '/modulos/vigilancia-epidemiologica?view=mapa', category: 'MAPEAMENTO', icon: 'Map' },
        { id: 'hotspots-epi', name: 'Hotspots', subtitle: 'Detecção espaço-temporal', path: '/modulos/vigilancia-epidemiologica?view=hotspots', category: 'ANALISE', icon: 'MapPin' },
        { id: 'qualidade-epi', name: 'Qualidade', subtitle: 'Duplicidades, atraso de notificação', path: '/modulos/vigilancia-epidemiologica?view=qualidade', category: 'CONTROLE', icon: 'CheckCircle' },
      ],
    },

    {
      id: 'e-denuncia',
      name: 'e‑Denúncia',
      description: 'Participação social e atividades de campo',
      path: '/denuncia',
      icon: 'Megaphone',
      group: 'Vigilância',
      functions: [
        { id: 'nova-denuncia', name: 'Nova Denúncia', path: '/denuncia', category: 'OPERACIONAL', icon: 'Plus' },
        { id: 'consultar-protocolo', name: 'Consultar Protocolo', path: '/denuncia/consultar/:protocolo', category: 'OPERACIONAL', icon: 'Search' },
        { id: 'painel-operacional-denuncia', name: 'Painel Operacional', path: '/modulos/e-denuncia?view=painel', category: 'OPERACIONAL', icon: 'LayoutGrid' },
        { id: 'integracao-atividades', name: 'Integração Atividades', path: '/modulos/e-denuncia?view=integration', category: 'OPERACIONAL', icon: 'Link' },
        { id: 'qualidade-auditoria-denuncia', name: 'Qualidade/Auditoria', path: '/modulos/e-denuncia?view=quality', category: 'CONTROLE', icon: 'Shield' },
      ],
    },

    // OPERAÇÕES
    {
      id: 'resposta-operacional',
      name: 'Resposta Operacional',
      description: 'Triagem, despacho e execução em campo',
      path: '/modulos/resposta-operacional',
      icon: 'Truck',
      group: 'Operações',
      roles: ['CAMPO', 'GESTOR'] as UserRole[],
      functions: [
        { id: 'triagem-despacho', name: 'Triagem & Despacho', subtitle: 'Regras de prioridade e distribuição', path: '/modulos/resposta-operacional?view=triagem', category: 'OPERACIONAL', icon: 'ClipboardList' },
        { id: 'planejamento-campo', name: 'Planejamento de Campo', subtitle: 'Roteirização, zonas-alvo', path: '/modulos/resposta-operacional?view=planejamento', category: 'OPERACIONAL', icon: 'Calendar' },
        { id: 'execucao-mobile', name: 'Execução (Mobile)', subtitle: 'Check-ins, coleta e fotos em campo', path: '/modulos/resposta-operacional?view=execucao', category: 'OPERACIONAL', icon: 'Smartphone' },
        { id: 'acompanhamento-atividades', name: 'Acompanhamento', subtitle: 'Status de atividades e produtividade', path: '/modulos/resposta-operacional?view=acompanhamento', category: 'OPERACIONAL', icon: 'CheckSquare' },
        { id: 'avaliacao-impacto', name: 'Avaliação de Impacto', subtitle: 'Antes/depois por área e período', path: '/modulos/resposta-operacional?view=impacto', category: 'ANALISE', icon: 'Target' },
      ],
    },

    // SISTEMA
    {
      id: 'administracao',
      name: 'Administração',
      description: 'Usuários, perfis e parâmetros do sistema',
      path: '/modulos/administracao',
      icon: 'Settings',
      group: 'Serviços Técnicos',
      roles: ['ADMIN', 'GESTOR'] as UserRole[],
      functions: [
        { id: 'usuarios-perfis', name: 'Usuários e Perfis', subtitle: 'Papéis (ADMIN/GESTOR/OPERADOR)', path: '/modulos/administracao?view=usuarios', category: 'CONTROLE', icon: 'Users' },
        { id: 'parametros-sistema', name: 'Parâmetros do Sistema', subtitle: 'Limiares, ícones, camadas default', path: '/modulos/administracao?view=parametros', category: 'CONTROLE', icon: 'Sliders' },
        { id: 'entidades', name: 'Entidades', subtitle: 'Municípios, unidades, equipes', path: '/modulos/administracao?view=entidades', category: 'CONTROLE', icon: 'Building2' },
        { id: 'auditoria-logs', name: 'Auditoria & Logs', subtitle: 'Trilhas e compliance', path: '/modulos/administracao?view=audit', category: 'CONTROLE', icon: 'FileSearch' },
      ],
    },

    {
      id: 'observabilidade',
      name: 'Observabilidade',
      description: 'Métricas, logs e qualidade operacional',
      path: '/modulos/observabilidade',
      icon: 'Gauge',
      badge: 'DEV',
      group: 'Serviços Técnicos',
      roles: ['ADMIN'] as UserRole[],
      functions: [
        { id: 'metricas', name: 'Métricas', subtitle: 'Prometheus/metrics de API e jobs', path: '/modulos/observabilidade?view=metricas', category: 'CONTROLE', icon: 'Activity' },
        { id: 'logs-sistema', name: 'Logs', subtitle: 'Estruturados e correlação por request-id', path: '/modulos/observabilidade?view=logs', category: 'CONTROLE', icon: 'FileText' },
        { id: 'saude-sistema', name: 'Saúde', subtitle: 'Health checks, filas e storage', path: '/modulos/observabilidade?view=health', category: 'CONTROLE', icon: 'HeartPulse' },
        { id: 'qualidade-dados', name: 'Qualidade de Dados', subtitle: 'Checks recorrentes e painéis', path: '/modulos/observabilidade?view=dataQuality', category: 'CONTROLE', icon: 'ShieldCheck' },
      ],
    },
  ],
}

export default NAVIGATION
