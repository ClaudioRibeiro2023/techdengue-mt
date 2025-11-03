# TechDengue MT — Matriz de Implantação Técnica Completa (Versão 2.0)

**Data de Criação**: 2025-11-02  
**Última Atualização**: 2025-11-02  
**Responsável**: Engenharia TechDengue MT  
**Status**: Documento Mestre de Planejamento

---

## 📑 ÍNDICE EXECUTIVO

1. [Objetivo e Escopo](#1-objetivo-do-documento)
2. [Análise do Estado Atual](#2-análise-do-estado-atual)
3. [Padrão Visual de Referência (WebMapa)](#3-padrão-visual-de-referência)
4. [Arquitetura Alvo](#4-arquitetura-de-alto-nível)
5. [Módulos e Aplicações Detalhadas](#5-módulos-e-aplicações-detalhadas)
   - 5.1 Mapa Vivo (WebGIS)
   - 5.2 Dashboard Epidemiológico
   - 5.3 Atividades de Campo
   - 5.4 Gestão de Evidências
   - 5.5 Relatórios EPI01
   - 5.6 Admin e RBAC
   - 5.7 ETL de Dados
6. [Padrões de UI/UX](#6-padrões-de-uiux)
7. [Integração com APIs](#7-integração-com-apis)
8. [Segurança e Conformidade](#8-segurança-e-conformidade)
9. [Observabilidade e SLOs](#9-observabilidade-e-slos)
10. [Estratégia de Testes](#10-estratégia-de-testes)
11. [Plano de Implementação](#11-plano-de-implementação)
12. [Critérios de Aceite](#12-critérios-de-aceite)

---

## 1) OBJETIVO DO DOCUMENTO

Este documento estabelece a **matriz única e detalhada** de TUDO que precisa ser entregue para a aplicação final do TechDengue MT em ambiente de produção real, cobrindo:

### Escopo de Cobertura

✅ **Requisitos Funcionais** - Todas as funcionalidades de negócio por módulo  
✅ **Requisitos Não-Funcionais** - Performance, segurança, disponibilidade  
✅ **Arquitetura de Software** - Frontend, Backend, Data Layer, Infra  
✅ **Experiência do Usuário** - Telas, fluxos, padrões visuais  
✅ **Integrações** - APIs, serviços, dependências externas  
✅ **Segurança** - Autenticação, autorização, proteções  
✅ **Observabilidade** - Métricas, logs, alertas, SLOs  
✅ **Testes** - Unitários, integração, E2E, performance  
✅ **Critérios de Aceite** - Definição clara de "pronto" por módulo

### Fontes de Informação

Este documento foi construído com base em análise profunda de:

1. **Documentação TechDengue MT** (15 documentos principais)
   - REPO_STATUS_TECNICO.md
   - ROADMAP_VISUAL.md
   - M1_GUIA_COMPLETO.md
   - M2_API_REFERENCE.md
   - M1.3_DASHBOARD_README.md
   - M1.4_RELATORIO_EPI01_README.md
   - FRONTEND_PWA_README.md
   - HARDENING_SECURITY_README.md
   - DEPLOY_GUIDE.md
   - E outros 6 documentos técnicos

2. **Código-Fonte Existente**
   - Backend: campo-api, epi-api, relatorios-api
   - Frontend: estrutura React + TS
   - Infraestrutura: Docker Compose, CI/CD, Monitoring

3. **Aplicação de Referência Visual**
   - WebMapa Conta Ovos (webmapa-conta-ovos)
   - Análise de 4 componentes principais:
     - TopBar.js (241 linhas)
     - WebMapaMenu.js (35.598 linhas)
     - AdvancedFiltersPanel.js (26.342 linhas)
     - DataPanel.js (795 linhas)

---

## 2) ANÁLISE DO ESTADO ATUAL

### 2.1) O Que Já Está Pronto (60% Completo)

#### ✅ Backend APIs (100% - Production Ready)

**Campo API** (5.500 linhas, 12 endpoints):
- CRUD completo de Atividades (6 endpoints)
- Upload de Evidências com S3/MinIO (4 endpoints)
- Relatórios EVD01 em PDF/A-1 (2 endpoints)
- Sync Service com resolução de conflitos
- 30 testes automatizados (94% passing)

**EPI API** (implementação parcial):
- ETL SINAN/LIRAa (schemas + services prontos)
- Backend de Mapa (camadas GeoJSON, heatmap, estatísticas)
- Endpoints prontos:
  - GET /api/mapa/camadas
  - GET /api/mapa/heatmap
  - GET /api/mapa/estatisticas
  - GET /api/mapa/series-temporais/{codigo_ibge}
  - GET /api/mapa/municipios

**Dashboard API** (100%):
- GET /api/indicadores/kpis
- GET /api/indicadores/series-temporais
- GET /api/indicadores/top

**Relatórios API** (100%):
- POST /api/relatorios/epi01
- GET /api/relatorios/epi01/{id}
- GET /api/relatorios/epi01/download/{id}/{formato}
- Geração de PDF com gráficos embarcados
- Export CSV
- Hash SHA-256 para integridade

#### ✅ Infraestrutura e DevOps (100%)

- Docker Compose (main + monitoring)
- PostgreSQL + TimescaleDB + PostGIS
- 11 Migrações Flyway versionadas
- MinIO/S3 para evidências
- Keycloak OIDC configurado
- Redis para cache e jobs
- Celery com 8 background tasks
- GitHub Actions CI/CD
- Observabilidade completa:
  - Prometheus (métricas)
  - Grafana (dashboards)
  - Loki (logs centralizados)
  - Alertmanager (25+ alertas)

#### ⚠️ Frontend React (15% - Estrutura Básica)

**O que existe**:
- Estrutura Vite + React 18 + TypeScript
- TailwindCSS configurado
- React Router v6 com rotas
- AuthContext (Keycloak OIDC)
- ProtectedRoute component
- MainLayout básico
- Modo demo reversível (VITE_DEMO_MODE)
- PWA manifest e ícones
- Alguns componentes:
  - KPICards.tsx
  - TimeSeriesChart.tsx
  - TopNChart.tsx

**O que falta** (85%):
- ❌ Páginas de negócio completas (apenas placeholders)
- ❌ Mapa interativo com Leaflet
- ❌ Filtros avançados (padrão WebMapa)
- ❌ Painel de dados
- ❌ Service Workers para offline
- ❌ IndexedDB para sync
- ❌ Integração real com APIs
- ❌ Testes E2E

### 2.2) Gaps Críticos Identificados

| Área | Status | Gap | Prioridade |
|------|--------|-----|------------|
| **Mapa Vivo** | 0% | Toda implementação frontend | 🔴 CRÍTICA |
| **Filtros Avançados** | 0% | Padrão WebMapa não aplicado | 🔴 CRÍTICA |
| **Dashboard EPI Frontend** | 20% | Integração com APIs real | 🔴 CRÍTICA |
| **Atividades Frontend** | 5% | UI completa + integração | 🟠 ALTA |
| **Evidências Frontend** | 5% | Upload, preview, validação | 🟠 ALTA |
| **PWA Offline** | 0% | Service Worker + IndexedDB | 🟠 ALTA |
| **Admin RBAC** | 0% | Gestão de usuários/roles | 🟡 MÉDIA |
| **Testes E2E** | 0% | Playwright suite completa | 🟡 MÉDIA |

---

## 3) PADRÃO VISUAL DE REFERÊNCIA (WebMapa Conta Ovos)

### 3.1) Análise Profunda do WebMapa

O WebMapa Conta Ovos é uma aplicação WebGIS de produção consolidada com **97.800+ linhas de código** (componentes principais analisados), representando uma implementação madura de vigilância epidemiológica espacial. A análise profunda revelou os seguintes padrões de excelência:

#### Componentes de Navegação Analisados

**TopBar.js** (241 linhas):
```javascript
// Estrutura:
- Breadcrumb hierárquico (SIVEPI > Monitoramento > Vigilância)
- Botões de ação rápida com estados (ativo/inativo)
- Contador de registros em tempo real
- Versão da aplicação
- Design: altura fixa 64px, shadow sutil, cor #FFFFFF
```

**Características TopBar**:
- Botão "Filtros": toggle do painel direito, cor primária #0087A8 quando ativo
- Botão "Análise": alterna para dashboard, estados visuais com hover
- Botão "Dados": abre DataPanel, design consistente
- Estados disabled com opacity 0.6 quando sem dados
- Transições suaves (0.2s) em todos os estados

**WebMapaMenu.js** (35.598 linhas - menu lateral esquerdo):
```javascript
// Estrutura:
- Sidebar colapsável (80px collapsed, 280px expanded)
- 8 visualizações principais: map, clusters, heatmap, hotspots, riskZones, layers, measurements, dashboard
- Controles detalhados por camada:
  * Heatmap: intensity (slider 0-2), radius (5-50px), blur (5-30px), gradient (4 presets)
  * Hotspots: threshold (0-1), gridSize, temporal weighting, max count
  * RiskZones: gridSize, thresholdFraction, temporal, maxZones
- Persistência de estados no localStorage
- Ícones Lucide React (Map, Layers, BarChart3, Activity, etc.)
```

**AdvancedFiltersPanel.js** (26.342 linhas - painel direito):
```javascript
// Estrutura principal:
- Width: 320px expandido, 80px collapsed
- Seções organizadas:
  1. Período (ano, mês, semana epidemiológica)
  2. Geografia (municípios, bairros com busca)
  3. Níveis de risco (checkboxes coloridos: zero/baixo/médio/alto/crítico)
  4. Métricas numéricas (min/max ovos ou casos)
- Contador de filtros ativos (badge no header)
- Botão "Limpar filtros"
- Search bar para bairros (filtro em tempo real)
- Persistência automática (localStorage)
```

**Níveis de Risco (padrão visual)**:
| Nível | Cor Texto | Cor Background | Range |
|-------|-----------|----------------|-------|
| Zero | #10B981 | #D1FAE5 | 0 ovos/casos |
| Baixo | #3B82F6 | #DBEAFE | 1-15 |
| Médio | #F59E0B | #FEF3C7 | 16-40 |
| Alto | #EF4444 | #FEE2E2 | 41-80 |
| Crítico | #DC2626 | #FEE2E2 | 81+ |

**DataPanel.js** (795 linhas - painel de métricas):
```javascript
// Estrutura:
- Agrupamento por ovitrampa única (Map para deduplicação)
- Métricas calculadas:
  * Total de ovitrampas/pontos únicos
  * Total de ovos/casos
  * Média por armadilha
  * Taxa de positividade (%)
  * Distribuição por nível de risco
- Comparação temporal com período anterior
- CompactVariationBadge (↑↓→ com %)
- SimpleBarChart (distribuição de risco)
- Botão export CSV
- Selector de janela temporal (week/month/quarter/year)
```

#### Padrões de Interação Identificados

1. **Estados Visuais Consistentes**:
   - Default: border #e5e7eb, background #FFFFFF
   - Hover: background #F9FAFB, border darker
   - Active: background #0087A8, color #FFFFFF, shadow elevado
   - Disabled: opacity 0.6, cursor not-allowed

2. **Transições Padronizadas**:
   - Panels: 300ms cubic-bezier(0.4, 0, 0.2, 1)
   - Buttons: 200ms ease
   - Hovers: 150ms ease-in-out

3. **Responsividade**:
   - Breakpoints: collapsed sidebars em < 1024px
   - Touch-friendly: botões mínimo 40x40px
   - Font sizes: 12-16px (14px padrão)

4. **Persistência de Estado**:
   - localStorage keys: webmapa_preferences, webmapa_filters, webmapa_panels
   - Formato JSON com versioning
   - Restore automático no mount

### 3.2) Adaptação para TechDengue MT

#### Componentes a Portar (Priorização)

**Fase 1 - Core UI** (prioridade CRÍTICA):
1. TopBar → `src/components/navigation/TopBar.tsx` (converter de .js)
2. AdvancedFiltersPanel → `src/components/filters/AdvancedFiltersPanel.tsx`
3. DataPanel → `src/components/data/DataPanel.tsx`
4. WebMapaMenu → `src/components/navigation/SidebarMenu.tsx` (simplificar)

**Fase 2 - Camadas de Mapa** (prioridade ALTA):
5. IntelligentClusterLayer → usar react-leaflet + custom logic
6. HeatMapLayer → leaflet.heat wrapper
7. HotspotsAnalysis → KDE implementation
8. RiskZones → buffer zones + classification
9. MeasurementTools → leaflet-draw integration

**Fase 3 - Hooks e Contextos** (prioridade ALTA):
10. useLocalStorage (persistência)
11. useFilters (lógica de filtros)
12. useTemporalComparison (comparação períodos)
13. WebMapaContext → MapContext (provider de dados)

#### Customizações Específicas TechDengue

**Centro e Zoom do Mapa**:
```typescript
// src/config/mapConfig.ts
export const MAP_CONFIG = {
  center: [-15.601411, -56.097892], // Cuiabá, MT
  zoom: 7, // Estado completo
  minZoom: 6,
  maxZoom: 18,
  bounds: [
    [-18.039, -61.628], // SW de MT
    [-7.348, -50.229]   // NE de MT
  ]
}
```

**Cores do Tema TechDengue** (manter consistência):
```typescript
// src/config/theme.ts
export const brandColors = {
  primary: '#2196F3',      // Azul TechDengue
  secondary: '#0087A8',    // Azul secundário
  success: '#4CAF50',
  warning: '#FFC107',
  danger: '#F44336',
  surface: '#FFFFFF',
  border: '#e5e7eb',
  textPrimary: '#1f2937',
  textSecondary: '#6b7280'
}
```

**Filtros Adaptados**:
- Ano: 2020-2026 (range epidemiológico MT)
- Municípios: 141 municípios de MT (via API /api/mapa/municipios)
- Doenças: DENGUE, ZIKA, CHIKUNGUNYA, FEBRE_AMARELA
- Métricas: casos confirmados, óbitos, incidência/100k

---

## 4) ARQUITETURA DE ALTO NÍVEL (Estado Alvo)

- Top Bar fixa: botões rápidos (Filtros, Camadas, Análise/Dashboard, Dados), contadores e versão.
- Menu lateral esquerdo (WebMapaMenu):
  - Alternância de visualizações: map, clusters, heatmap, hotspots, riskZones, layers, measurements
  - Controles de heatmap e hotspots (intensidade, raio, blur, gradient, thresholds)
  - Controles de risk zones
  - Toggles de camadas
- Painel de filtros à direita (AdvancedFiltersPanel): período (ano/mês/semana), geografia (município/bairro), níveis de risco e métricas numéricas.
- Painel de dados (DataPanel): visão tabular e métricas (distribuições, KPIs auxiliares).
- Área central: mapa (Leaflet) e/ou dashboards.
- Persistência de preferências (localStorage) e reatividade.

Aplicação direta no TechDengue:
- Rota /mapa: importar estrutura WebMapa (TS/JS compatível) e integrar com APIs da epi-api.
- Rota /dashboard: layout herdado (cards, gráficos), com padrão de filtros e top bar.

---

## 5) Módulos/aplicações e escopo funcional (produção)

A seguir, matriz por aplicação com: objetivo, público/roles, funcionalidades, telas/UX, integração com APIs, segurança, observabilidade, testes e critérios de aceite.

### 5.1) Mapa Vivo (WebGIS)

- Objetivo: Visualizar situação epidemiológica espacial (incidência, casos, calor, hotspots, zonas de risco) com filtros temporais e regionais.
- Públicos/roles: VIGILANCIA, GESTOR, ADMIN. (CAMPO: leitura)
- Funcionalidades:
  1. Camadas base OSM, clusters inteligentes, heatmap, hotspots (KDE) e zonas de risco.
  2. Filtros: ano, mês, semana epidemiológica, município/bairro, níveis de risco.
  3. Painel de dados com contagens/métricas e export CSV (somente ADMIN/GESTOR).
  4. Ferramentas: medição distância/área, alternância de camadas.
  5. Timeline temporal (auto-play) opcional.
- Telas/UX:
  - TopBar (Filtros/Layers/Analisar/Dados) + WebMapaMenu (esquerda) + FiltersPanel (direita) + DataPanel (inferência) + Mapa central.
- Integração com APIs:
  - epi-api:
    - GET /api/mapa/camadas
    - GET /api/mapa/heatmap
    - GET /api/mapa/estatisticas
    - GET /api/mapa/series-temporais/{codigo_ibge}
    - GET /api/mapa/municipios
- Segurança:
  - Rotas protegidas por OIDC; exportações restritas a GESTOR/ADMIN.
  - Sanitização de filtros; rate limit no backend.
- Observabilidade:
  - Métricas de tempo de resposta p95 ≤ 4s (SLO);
  - Logs de filtros (sem PII), traços por requisição.
- Testes:
  - E2E: carregamento mapa, aplicação de filtros, alternância de camadas, export.
  - Performance (k6): camadas/heatmap/municipios p95 ≤ 4s.
- Critérios de aceite:
  - Renderiza 5 camadas, filtros operacionais, export CSV funcional, sem erros de console.

### 5.2) Dashboard EPI

- Objetivo: KPIs, séries temporais e ranking por município.
- Públicos/roles: VIGILANCIA, GESTOR, ADMIN.
- Funcionalidades:
  1. KPIs (casos, incidência, variação %) com período selecionável.
  2. Séries temporais por doença/município.
  3. Top N municípios (casos/ incidência) e drill-down.
  4. Export CSV dos datasets exibidos.
- Telas/UX:
  - Cards KPI + gráficos line/bar (Chart.js) + filtros horizontais e alinhamento com TopBar do WebMapa.
- Integração com APIs (a consolidar):
  - Sugeridos: GET /api/indicadores/kpis, /series-temporais, /top (padronizar na epi-api).
- Segurança/Observabilidade/Testes/ACE como Mapa, com variações específicas (dashboard-load p95 ≤ 4s).

### 5.3) Relatórios EPI01 (PDF + CSV)

- Objetivo: Gerar relatórios epidemiológicos oficiais.
- Públicos/roles: GESTOR, ADMIN.
- Funcionalidades:
  1. Formulário (período, município, doença) → geração assíncrona.
  2. Download de PDF/A-1 e CSV; metadados com hash e QR.
- Integração com APIs:
  - relatorios-api:
    - GET /api/relatorios/epi01
    - GET /api/relatorios/epi01/download/{id}
- ACE: Geração em < 30s; verificação de hash consistente.

### 5.4) Atividades de Campo & Evidências

- Objetivo: Registrar, consultar e auditar atividades e evidências.
- Públicos/roles: CAMPO, VIGILANCIA, GESTOR, ADMIN.
- Funcionalidades:
  1. Listagem de atividades com filtros; detalhes e timeline.
  2. Upload de evidências (foto, vídeo, docs) com metadados (EXIF, hash SHA-256) via MinIO/S3.
  3. Estados da atividade e relatórios EVD01.
- Integração com APIs (campo-api): CRUDs já existentes (ver docs/M2_*).
- PWA: fila offline, background sync para uploads pendentes.

### 5.5) Admin & RBAC

- Objetivo: Gerir usuários, papéis, parâmetros e integrações.
- Público/roles: ADMIN.
- Funcionalidades:
  1. Visualização de usuários, atribuição de roles (Keycloak Admin API).
  2. Parâmetros operacionais (ex.: thresholds de risco, limites de exportação).
  3. Auditoria e trilhas (logs e eventos).

---

## 6) Integração visual do WebMapa no TechDengue

- Estratégia: portar o núcleo WebMapa (componentes JS) para um módulo do frontend (`src/modules/webmapa/`), mantendo compatibilidade com TS via declarações mínimas (d.ts) e/ou conversão gradual.
- Componentes alvo a portar:
  - navigation: TopBar, WebMapaMenu
  - sidebar/filters: AdvancedFiltersPanel
  - map layers: IntelligentClusterLayer, HeatMapLayer, HotspotsAnalysis, RiskZones, MeasurementTools
  - data: DataPanel
  - contexts/hooks: WebMapaContext, useAnalysis, useLocalStorage
  - utils: applyFilters, validation, extractors
- Adaptações:
  - Configuração de centro/zoom para Mato Grosso (Cuiabá/MT) e municípios MT.
  - Filtros alinhados com a epi-api (parâmetros aceitos pelos endpoints)
  - Exportações com cabeçalhos e regionalização pt-BR.
  - Tema/cores ajustadas ao Design System atual.
- Dependências:
  - leaflet, leaflet.heat, leaflet.markercluster, react-leaflet, lucide-react
- Riscos e mitigação:
  - Performance: manter amostragem inteligente e debounce (como no WebMapa). SLO p95 ≤ 4s.
  - Tipagem: iniciar com JSDoc e tipos auxiliares, converter gradualmente.

---

## 7) Segurança e conformidade

- Autenticação: OIDC Keycloak, tokens renováveis, logout, roles por rota.
- Autorização: menu e ações condicionados às roles; exports restritos.
- CORS: liberar origem do domínio oficial Netlify/domínio próprio.
- Headers: já definidos no netlify.toml; manter HSTS e X-Content-Type.
- Dados sensíveis: não logar PII; mascaramento quando necessário.

---

## 8) Observabilidade e SLOs

- Métricas (Prometheus): latência p95 de endpoints-chave (mapa, KPIs, relatórios), disponibilidade ≥ 99.9%, error rate < 1%.
- Logs centralizados (Loki): correlação por request-id.
- Dashboards Grafana prontos para SLOs; alertas via Alertmanager (Slack/Email).

---

## 9) Testes e qualidade

- E2E (Playwright): fluxos mapa, dashboard, filtros, export, login/logout.
- Performance (k6): dashboards, mapa e ETL conforme docs/TESTES_PERFORMANCE_README.md.
- Unit/integração: componentes de UI (Vitest/RTL) e serviços.
- Critério de passagem: sem regressões, sem erros de console, builds verdes.

---

## 10) Entregáveis por etapa (sequência)

1. Integração WebMapa no /mapa (front) — 1,5 semana
   - Portar componentes, configurar Leaflet e camadas, filtros básicos → epi-api
   - DataPanel e export CSV
   - Observabilidade client-side (web-vitals) e logging leve
2. Dashboard EPI — 1 semana
   - KPIs + séries + TopN com endpoints consolidados
   - Exports e drill-down
3. Relatórios EPI01 — 0,5 semana
   - UI + integrações relatorios-api (PDF/CSV)
4. Campo & Evidências (front) — 1,5 semana
   - Lista/detalhes/form + upload S3 + PWA queue
5. Admin & RBAC — 0,5 semana
   - Tela de usuários/roles (read-only) + parâmetros
6. Produção com Autenticação
   - Desativar DEMO_MODE; configurar Keycloak/URLs públicas; políticas de CORS
7. Testes E2E/Performance e Hardening — 1 semana
   - Playwright + k6 + ajustes finais observabilidade e segurança

---

## 11) Mapeamento de variáveis de ambiente (produção)

- VITE_API_URL=https://api.techdengue.mt.gov.br/api
- VITE_KEYCLOAK_URL=https://keycloak.techdengue.mt.gov.br
- VITE_KEYCLOAK_REALM=techdengue
- VITE_KEYCLOAK_CLIENT_ID=techdengue-frontend
- VITE_DEMO_MODE=false

---

## 12) Critérios gerais de aceite (produção)

- Login OIDC e rotas protegidas ativas; RBAC efetivo.
- Mapa Vivo: camadas, filtros, painéis e export funcionais; p95 ≤ 4s.
- Dashboard: KPIs, séries e TopN funcionais; p95 ≤ 4s.
- Relatórios: geração e download de PDF/CSV com hash/QR.
- Campo: criação/consulta de atividades, upload de evidências com integridade.
- Observabilidade e alertas ativos; CI/CD verde; documentação atualizada.

---

## 13) Anexos e referências

- TechDengue MT: docs/REPO_STATUS_TECNICO.md, docs/ROADMAP_VISUAL.md, docs/DEPLOY_GUIDE.md, docs/TESTES_PERFORMANCE_README.md
- WebMapa Conta Ovos: README, WebMapaContaOvosMain.js e módulos descritos

---

## 14) Decisões em aberto (para validação)

- Padronização de gráficos: manter Chart.js em todo o projeto ou aceitar Recharts apenas no WebMapa? (sugestão: manter Chart.js para reduzir dependências)
- Estratégia de portabilidade JS→TS do WebMapa (converter gradualmente com d.ts iniciais)
- Domínio final e certificados (Netlify + DNS)

---

## 15) Próxima ação sugerida

Aprovar a Etapa 1 (Integração WebMapa no /mapa) e iniciar o porte dos componentes com ligação às APIs da epi-api. Em paralelo, iniciar consolidação dos endpoints de indicadores do Dashboard EPI na epi-api.
