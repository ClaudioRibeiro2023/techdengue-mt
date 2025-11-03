import type { NavigationMap } from './types'

export const NAVIGATION: NavigationMap = {
  modules: [
    {
      id: 'mapa-vivo',
      name: 'Mapa Vivo',
      description: 'Interface de visualização geoespacial',
      path: '/mapa',
      topNav: true,
      functions: [
        { id: 'mapa-principal', name: 'Mapa Principal', path: '/mapa', category: 'MAPEAMENTO' },
        { id: 'mapa-calor', name: 'Mapa de Calor', path: '/mapa?view=heatmap', category: 'ANALISE' },
        { id: 'hotspots', name: 'Hotspots', path: '/mapa?view=hotspots', category: 'ANALISE' },
        { id: 'zonas-risco', name: 'Zonas de Risco', path: '/mapa?view=risk', category: 'ANALISE' },
      ],
    },
    {
      id: 'dashboard-executivo',
      name: 'Dashboard',
      description: 'Painel consolidado de indicadores',
      path: '/dashboard',
      topNav: true,
      functions: [
        { id: 'visao-geral', name: 'Visão Geral', path: '/dashboard', category: 'INDICADORES' },
      ],
    },
    {
      id: 'etl-integracao',
      name: 'ETL & Integração',
      description: 'Importadores e tratamento de dados',
      path: '/etl',
      topNav: true,
      functions: [
        { id: 'etl-sinan', name: 'Importar SINAN', path: '/etl?src=sinan', category: 'OPERACIONAL' },
        { id: 'etl-liraa', name: 'Importar LIRAa', path: '/etl?src=liraa', category: 'OPERACIONAL' },
      ],
    },
    {
      id: 'relatorios',
      name: 'Relatórios',
      description: 'Relatórios e exportações',
      path: '/relatorios',
      topNav: true,
      functions: [
        { id: 'epi01', name: 'EPI-01', path: '/relatorios?doc=epi01', category: 'INDICADORES' },
      ],
    },
    {
      id: 'vigilancia-entomologica',
      name: 'Vigilância Entomológica',
      description: 'Monitoramento de populações vetoriais',
      path: '/modulos/vigilancia-entomologica',
      functions: [
        { id: 'visao-geral-entomo', name: 'Visão Geral', path: '/modulos/vigilancia-entomologica?view=overview', category: 'ANALISE' },
        { id: 'analise-sazonal', name: 'Análise Sazonal', path: '/modulos/vigilancia-entomologica?view=sazonal', category: 'ANALISE' },
        { id: 'ovitrampas', name: 'Ovitrampas', path: '/modulos/vigilancia-entomologica?view=ovitrampas', category: 'MAPEAMENTO' },
        { id: 'indices', name: 'Índices (IPO/IDO/IMO)', path: '/modulos/vigilancia-entomologica?view=indices', category: 'INDICADORES' },
        { id: 'qualidade-entomo', name: 'Qualidade', path: '/modulos/vigilancia-entomologica?view=qualidade', category: 'CONTROLE' },
      ],
    },
    {
      id: 'vigilancia-epidemiologica',
      name: 'Vigilância Epidemiológica',
      description: 'Casos, incidência e hotspots',
      path: '/modulos/vigilancia-epidemiologica',
      functions: [
        { id: 'visao-geral-epi', name: 'Visão Geral', path: '/modulos/vigilancia-epidemiologica?view=overview', category: 'ANALISE' },
        { id: 'series-temporais', name: 'Séries Temporais', path: '/modulos/vigilancia-epidemiologica?view=temporal', category: 'ANALISE' },
        { id: 'mapa-incidencia', name: 'Mapa de Incidência', path: '/modulos/vigilancia-epidemiologica?view=mapa', category: 'MAPEAMENTO' },
        { id: 'hotspots-epi', name: 'Hotspots', path: '/modulos/vigilancia-epidemiologica?view=hotspots', category: 'ANALISE' },
        { id: 'qualidade-epi', name: 'Qualidade', path: '/modulos/vigilancia-epidemiologica?view=qualidade', category: 'CONTROLE' },
      ],
    },
    {
      id: 'e-denuncia',
      name: 'e‑Denúncia',
      description: 'Participação social e atividades',
      path: '/denuncia',
      functions: [
        { id: 'nova-denuncia', name: 'Nova Denúncia', path: '/denuncia', category: 'OPERACIONAL' },
        { id: 'consultar-protocolo', name: 'Consultar Protocolo', path: '/denuncia/consultar/:protocolo', category: 'OPERACIONAL' },
        { id: 'painel-operacional', name: 'Painel Operacional', path: '/modulos/e-denuncia?view=painel', category: 'OPERACIONAL' },
      ],
    },
    {
      id: 'resposta-operacional',
      name: 'Resposta Operacional',
      description: 'Triagem, despacho e execução em campo',
      path: '/modulos/resposta-operacional',
      functions: [
        { id: 'triagem', name: 'Triagem & Despacho', path: '/modulos/resposta-operacional?view=triagem', category: 'OPERACIONAL' },
        { id: 'planejamento', name: 'Planejamento de Campo', path: '/modulos/resposta-operacional?view=planejamento', category: 'OPERACIONAL' },
        { id: 'execucao', name: 'Execução (Mobile)', path: '/modulos/resposta-operacional?view=execucao', category: 'OPERACIONAL' },
        { id: 'acompanhamento', name: 'Acompanhamento', path: '/modulos/resposta-operacional?view=acompanhamento', category: 'OPERACIONAL' },
      ],
    },
    {
      id: 'previsao-simulacao',
      name: 'Previsão & Simulação',
      description: 'Nowcasting, Rt e cenários',
      path: '/modulos/previsao-simulacao',
      functions: [
        { id: 'nowcasting', name: 'Nowcasting / Rt', path: '/modulos/previsao-simulacao?view=nowcasting', category: 'ANALISE' },
        { id: 'previsao', name: 'Previsão 2–4 semanas', path: '/modulos/previsao-simulacao?view=forecast', category: 'ANALISE' },
        { id: 'cenarios', name: 'Cenários de Intervenção', path: '/modulos/previsao-simulacao?view=cenarios', category: 'ANALISE' },
      ],
    },
    {
      id: 'administracao',
      name: 'Administração',
      description: 'Usuários, perfis e parâmetros',
      path: '/modulos/administracao',
      functions: [
        { id: 'usuarios', name: 'Usuários e Perfis', path: '/modulos/administracao?view=usuarios', category: 'CONTROLE' },
        { id: 'parametros', name: 'Parâmetros', path: '/modulos/administracao?view=parametros', category: 'CONTROLE' },
        { id: 'entidades', name: 'Entidades', path: '/modulos/administracao?view=entidades', category: 'CONTROLE' },
      ],
    },
    {
      id: 'observabilidade',
      name: 'Observabilidade',
      description: 'Métricas, logs e saúde',
      path: '/modulos/observabilidade',
      functions: [
        { id: 'metricas', name: 'Métricas', path: '/modulos/observabilidade?view=metricas', category: 'CONTROLE' },
        { id: 'logs', name: 'Logs', path: '/modulos/observabilidade?view=logs', category: 'CONTROLE' },
        { id: 'saude', name: 'Saúde', path: '/modulos/observabilidade?view=health', category: 'CONTROLE' },
      ],
    },
  ],
}

export default NAVIGATION
