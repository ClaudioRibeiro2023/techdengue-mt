import type { NavigationMap } from './types'

export const NAVIGATION: NavigationMap = {
  modules: [
    {
      id: 'mapa-vivo',
      name: 'Mapa Vivo',
      description: 'Interface de visualização geoespacial',
      path: '/mapa',
      topNav: true,
      icon: 'Map',
      functions: [
        { id: 'mapa-principal', name: 'Mapa Principal', path: '/mapa', category: 'MAPEAMENTO', icon: 'Map' },
        { id: 'mapa-calor', name: 'Mapa de Calor', path: '/mapa?view=heatmap', category: 'ANALISE', icon: 'Flame' },
        { id: 'hotspots', name: 'Hotspots', path: '/mapa?view=hotspots', category: 'ANALISE', icon: 'MapPin' },
        { id: 'zonas-risco', name: 'Zonas de Risco', path: '/mapa?view=risk', category: 'ANALISE', icon: 'AlertTriangle' },
      ],
    },
    {
      id: 'dashboard-executivo',
      name: 'Dashboard',
      description: 'Painel consolidado de indicadores',
      path: '/dashboard',
      topNav: true,
      icon: 'LayoutDashboard',
      functions: [
        { id: 'visao-geral', name: 'Visão Geral', path: '/dashboard', category: 'INDICADORES', icon: 'Eye' },
      ],
    },
    {
      id: 'etl-integracao',
      name: 'ETL & Integração',
      description: 'Importadores e tratamento de dados',
      path: '/etl',
      topNav: true,
      icon: 'Database',
      functions: [
        { id: 'etl-sinan', name: 'Importar SINAN', path: '/etl?src=sinan', category: 'OPERACIONAL', icon: 'Upload' },
        { id: 'etl-liraa', name: 'Importar LIRAa', path: '/etl?src=liraa', category: 'OPERACIONAL', icon: 'Upload' },
      ],
    },
    {
      id: 'relatorios',
      name: 'Relatórios',
      description: 'Relatórios e exportações',
      path: '/relatorios',
      topNav: true,
      icon: 'FileText',
      functions: [
        { id: 'epi01', name: 'EPI-01', path: '/relatorios?doc=epi01', category: 'INDICADORES', icon: 'FileSpreadsheet' },
      ],
    },
    {
      id: 'vigilancia-entomologica',
      name: 'Vigilância Entomológica',
      description: 'Monitoramento de populações vetoriais',
      path: '/modulos/vigilancia-entomologica',
      icon: 'Bug',
      functions: [
        { id: 'visao-geral-entomo', name: 'Visão Geral', path: '/modulos/vigilancia-entomologica?view=overview', category: 'ANALISE', icon: 'Eye' },
        { id: 'analise-sazonal', name: 'Análise Sazonal', path: '/modulos/vigilancia-entomologica?view=sazonal', category: 'ANALISE', icon: 'Calendar' },
        { id: 'ovitrampas', name: 'Ovitrampas', path: '/modulos/vigilancia-entomologica?view=ovitrampas', category: 'MAPEAMENTO', icon: 'MapPinned' },
        { id: 'indices', name: 'Índices (IPO/IDO/IMO)', path: '/modulos/vigilancia-entomologica?view=indices', category: 'INDICADORES', icon: 'TrendingUp' },
        { id: 'qualidade-entomo', name: 'Qualidade', path: '/modulos/vigilancia-entomologica?view=qualidade', category: 'CONTROLE', icon: 'CheckCircle' },
      ],
    },
    {
      id: 'vigilancia-epidemiologica',
      name: 'Vigilância Epidemiológica',
      description: 'Casos, incidência e hotspots',
      path: '/modulos/vigilancia-epidemiologica',
      icon: 'Activity',
      functions: [
        { id: 'visao-geral-epi', name: 'Visão Geral', path: '/modulos/vigilancia-epidemiologica?view=overview', category: 'ANALISE', icon: 'Eye' },
        { id: 'series-temporais', name: 'Séries Temporais', path: '/modulos/vigilancia-epidemiologica?view=temporal', category: 'ANALISE', icon: 'LineChart' },
        { id: 'mapa-incidencia', name: 'Mapa de Incidência', path: '/modulos/vigilancia-epidemiologica?view=mapa', category: 'MAPEAMENTO', icon: 'Map' },
        { id: 'hotspots-epi', name: 'Hotspots', path: '/modulos/vigilancia-epidemiologica?view=hotspots', category: 'ANALISE', icon: 'MapPin' },
        { id: 'qualidade-epi', name: 'Qualidade', path: '/modulos/vigilancia-epidemiologica?view=qualidade', category: 'CONTROLE', icon: 'CheckCircle' },
      ],
    },
    {
      id: 'e-denuncia',
      name: 'e‑Denúncia',
      description: 'Participação social e atividades',
      path: '/denuncia',
      icon: 'MessageSquareWarning',
      functions: [
        { id: 'nova-denuncia', name: 'Nova Denúncia', path: '/denuncia', category: 'OPERACIONAL', icon: 'Plus' },
        { id: 'consultar-protocolo', name: 'Consultar Protocolo', path: '/denuncia/consultar/:protocolo', category: 'OPERACIONAL', icon: 'Search' },
        { id: 'painel-operacional', name: 'Painel Operacional', path: '/modulos/e-denuncia?view=painel', category: 'OPERACIONAL', icon: 'LayoutGrid' },
      ],
    },
    {
      id: 'resposta-operacional',
      name: 'Resposta Operacional',
      description: 'Triagem, despacho e execução em campo',
      path: '/modulos/resposta-operacional',
      icon: 'Truck',
      functions: [
        { id: 'triagem', name: 'Triagem & Despacho', path: '/modulos/resposta-operacional?view=triagem', category: 'OPERACIONAL', icon: 'ClipboardList' },
        { id: 'planejamento', name: 'Planejamento de Campo', path: '/modulos/resposta-operacional?view=planejamento', category: 'OPERACIONAL', icon: 'Calendar' },
        { id: 'execucao', name: 'Execução (Mobile)', path: '/modulos/resposta-operacional?view=execucao', category: 'OPERACIONAL', icon: 'Smartphone' },
        { id: 'acompanhamento', name: 'Acompanhamento', path: '/modulos/resposta-operacional?view=acompanhamento', category: 'OPERACIONAL', icon: 'CheckSquare' },
      ],
    },
    {
      id: 'previsao-simulacao',
      name: 'Previsão & Simulação',
      description: 'Nowcasting, Rt e cenários',
      path: '/modulos/previsao-simulacao',
      icon: 'Brain',
      functions: [
        { id: 'nowcasting', name: 'Nowcasting / Rt', path: '/modulos/previsao-simulacao?view=nowcasting', category: 'ANALISE', icon: 'Zap' },
        { id: 'previsao', name: 'Previsão 2–4 semanas', path: '/modulos/previsao-simulacao?view=forecast', category: 'ANALISE', icon: 'TrendingUp' },
        { id: 'cenarios', name: 'Cenários de Intervenção', path: '/modulos/previsao-simulacao?view=cenarios', category: 'ANALISE', icon: 'GitBranch' },
      ],
    },
    {
      id: 'administracao',
      name: 'Administração',
      description: 'Usuários, perfis e parâmetros',
      path: '/modulos/administracao',
      icon: 'Settings',
      functions: [
        { id: 'usuarios', name: 'Usuários e Perfis', path: '/modulos/administracao?view=usuarios', category: 'CONTROLE', icon: 'Users' },
        { id: 'parametros', name: 'Parâmetros', path: '/modulos/administracao?view=parametros', category: 'CONTROLE', icon: 'Sliders' },
        { id: 'entidades', name: 'Entidades', path: '/modulos/administracao?view=entidades', category: 'CONTROLE', icon: 'Building2' },
      ],
    },
    {
      id: 'observabilidade',
      name: 'Observabilidade',
      description: 'Métricas, logs e saúde',
      path: '/modulos/observabilidade',
      icon: 'BarChart3',
      functions: [
        { id: 'metricas', name: 'Métricas', path: '/modulos/observabilidade?view=metricas', category: 'CONTROLE', icon: 'Activity' },
        { id: 'logs', name: 'Logs', path: '/modulos/observabilidade?view=logs', category: 'CONTROLE', icon: 'FileText' },
        { id: 'saude', name: 'Saúde', path: '/modulos/observabilidade?view=health', category: 'CONTROLE', icon: 'HeartPulse' },
      ],
    },
  ],
}

export default NAVIGATION
