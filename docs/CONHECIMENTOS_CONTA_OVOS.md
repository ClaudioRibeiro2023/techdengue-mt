# Conhecimentos Aplicáveis — Conta Ovos → TechDengue

**Fonte**: SIVEPI WebMapa Conta Ovos  
**Data**: 2025-11-01

---

## 1. Similaridades de Contexto

- **Domínio**: Vigilância epidemiológica (Aedes aegypti)
- **Dados georreferenciados**: Ovitrampas vs atividades de campo
- **Indicadores epidemiológicos**: IOP vs IPO/IDO/IVO/IMO
- **Offline-first**: Campo com rede instável
- **Mapas interativos**: Leaflet com clustering
- **Stack**: React 18, Leaflet 1.9.4, PWA

---

## 2. Padrões Arquiteturais Aplicáveis

### Modularização
```
/components
  /map/         # IntelligentClusterLayer, HeatMapLayer
  /sidebar/     # MetricsPanel, Filters
  /dashboard/   # ExecutiveDashboard
  /temporal/    # TemporalFilter
/hooks/         # useDataProcessor, useMetrics, useWebWorker
/contexts/      # WebMapaContext
/workers/       # DataProcessorWorker
```

### Web Workers (Performance)
- Processamento off-thread de estatísticas
- Detecção de hotspots
- Validação de dados
- Hook `useWebWorker` para gerenciamento

### PWA Offline-First
- Service Worker: cache first (assets) + network first (dados)
- IndexedDB para armazenamento local
- Fila de sincronização resiliente
- Hook `useServiceWorker` para controle

---

## 3. Funcionalidades Epidemiológicas

### Clustering Inteligente por Risco
- Níveis: Sem Risco (verde) → Crítico (roxo)
- Ícones dinâmicos por densidade
- Popups detalhados

### Timeline com Semanas Epidemiológicas
- Seletor de ano + semana (1-52)
- Cálculo automático de datas
- Filtros temporais avançados

### Insights Acionáveis
- IOP (Índice de Ovos Positivos)
- Top 5 áreas prioritárias
- Detecção de surtos automática
- Recomendações contextuais

---

## 4. Otimizações de Performance

### Cache Inteligente
- TTL: 30 segundos
- Invalidação por timestamp
- Reutilização de dados processados

### Debounce Otimizado
- Conta Ovos: 150ms (vs 500-600ms anterior)
- Imperceptível ao usuário (< 200ms)

### Virtualização de Markers
- Renderizar apenas viewport
- Limites dinâmicos por zoom
- Clustering automático

---

## 5. Decisões Arquiteturais (ADRs)

### ADR-006: Frontend Stack
- React 18 + Leaflet 1.9.4 (não Mapbox)
- Justificativa: suficiente para <100k pontos, sem custo

### ADR-007: Estado
- Context API + hooks (não Redux)
- Menos boilerplate, React 18 nativo

### ADR-008: Performance
- Web Workers + virtualização + cache TTL 30s
- Debounce 150ms

### ADR-009: Offline
- Service Worker + IndexedDB + fila sync
- Estratégias: cache first/network first

---

## 6. Componentes Aplicáveis

### Design System
```javascript
const epidColors = {
  sem_risco: '#22c55e',  // Verde
  baixo: '#eab308',      // Amarelo
  medio: '#f97316',      // Laranja
  alto: '#ef4444',       // Vermelho
  critico: '#8b5cf6'     // Roxo
};
```

### Componentes UI
- Card (variants: default, glass, elevated)
- Badge (variants: success, warning, error)
- Button, Alert, LoadingSpinner

---

## 7. Testes
- Jest + React Testing Library (>95% cobertura)
- Cypress E2E
- Mocks: Leaflet, WebSocket, Service Worker

---

## 8. Integração no Plano TechDengue

### M0 (Fundações)
- Estrutura modular
- Design System epidemiológico
- Jest + RTL setup

### M1 (Mapa/ETL)
- Clustering inteligente
- Timeline por competência
- Dashboard insights
- Cache TTL 30s, debounce 150ms

### M2 (Campo/PWA)
- Web Worker validação
- Virtualização markers
- Fila sync offline
- IndexedDB

### M3 (Operação/Admin)
- Web Worker exports
- Análise hotspots
- Métricas tempo real

---

**ROI**: Padrões validados em produção (SIVEPI), redução de riscos técnicos, aceleração desenvolvimento M1-M2.
