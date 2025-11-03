# MATRIZ DETALHADA POR MÓDULO - TechDengue MT

**Documento Complementar à Matriz de Implantação Técnica v2.0**  
**Data**: 2025-11-02  
**Status**: Detalhamento Profundo de Cada Módulo/Aplicação

---

## 📋 SUMÁRIO EXECUTIVO

Este documento detalha profundamente cada módulo da aplicação TechDengue MT, incluindo:
- Requisitos funcionais e não-funcionais completos
- Especificações técnicas detalhadas
- Telas e fluxos de usuário
- Integrações com APIs
- Critérios de aceite por funcionalidade
- Estimativas de esforço

**Módulos Detalhados**:
1. Mapa Vivo (WebGIS) - 35 páginas
2. Dashboard Epidemiológico - 25 páginas
3. Atividades de Campo - 20 páginas
4. Gestão de Evidências - 18 páginas
5. Relatórios EPI01 - 15 páginas
6. ETL de Dados - 12 páginas
7. Admin e RBAC - 10 páginas

**Total**: ~135 páginas de especificação detalhada

---

## MÓDULO 1: MAPA VIVO (WebGIS)

### 1.1) Visão Geral

**Objetivo**: Visualização geoespacial em tempo real da situação epidemiológica de dengue, zika, chikungunya e febre amarela em Mato Grosso.

**Público-Alvo**:
- VIGILANCIA: visualizar, filtrar, analisar
- GESTOR: todas anteriores + export
- ADMIN: acesso total + config
- CAMPO: leitura limitada

**Complexidade**: 🔴 ALTA

**Estimativa**: 2-3 semanas (1 dev frontend + 1 dev GIS)

### 1.2) Funcionalidades Principais

#### F1.1 - Mapa Base Interativo
- Provider: OpenStreetMap
- Centro: Cuiabá (-15.601, -56.097)
- Zoom: 7 (inicial), 6-18 (range)
- Controles: zoom, pan, fullscreen, scale
- Bounds restritos a MT

#### F1.2 - Camada Choropleth (Incidência)
- 141 municípios coloridos por risco
- Classificação: BAIXO/MÉDIO/ALTO/MUITO_ALTO
- Popup com métricas detalhadas
- Hover effect

#### F1.3 - Heatmap (Densidade)
- Leaflet.heat com 3k pontos max
- Controles: intensity, radius, blur, gradient
- 4 gradientes: epidemiológico, térmico, fogo, mono
- Amostragem inteligente

#### F1.4 - Hotspots (KDE)
- Kernel Density Estimation
- Grid adaptativo por zoom
- Peso temporal (decay exponencial)
- Círculos duplos com scores

#### F1.5 - Zonas de Risco (Buffer)
- Buffer analysis (500m-2km)
- Score multi-fator
- Polígonos simplificados
- 4 níveis de risco

#### F1.6 - Painel de Filtros
- Período: ano/mês/semana
- Geografia: municípios/bairros
- Doença: DENGUE/ZIKA/CHIK/FA
- Níveis de risco
- Métricas numéricas

#### F1.7 - Painel de Dados
- Métricas agregadas
- Distribuição por risco
- Top 5 municípios
- Comparação temporal
- Export CSV

#### F1.8 - Ferramentas de Medição
- Medir distância (polyline)
- Medir área (polygon)
- Formato: km e km²

### 1.3) Integrações Backend

**epi-api** (http://localhost:8000/api):

```
GET /mapa/camadas
GET /mapa/heatmap
GET /mapa/estatisticas
GET /mapa/series-temporais/{codigo_ibge}
GET /mapa/municipios
```

### 1.4) Tecnologias

**Core**:
- React 18 + TypeScript
- react-leaflet ^4.2.1
- leaflet ^1.9.4
- leaflet.heat ^0.2.0
- leaflet.markercluster ^1.5.3

**Dependências**:
- axios (API calls)
- react-query (caching)
- zustand (state)
- lucide-react (icons)

### 1.5) Critérios de Aceite

✅ Mapa carrega em < 3s  
✅ 141 municípios renderizam corretamente  
✅ Filtros aplicam em < 500ms  
✅ Heatmap suporta 3k pontos sem lag  
✅ Hotspots calculam em < 2s  
✅ Zonas de risco geram em < 3s  
✅ Export CSV funcional  
✅ Persist filters em localStorage  
✅ Responsivo (desktop/tablet/mobile)  
✅ Sem erros de console

---

## MÓDULO 2: DASHBOARD EPIDEMIOLÓGICO

### 2.1) Visão Geral

**Objetivo**: Painéis executivos com KPIs, séries temporais e rankings para análise epidemiológica.

**Público-Alvo**: VIGILANCIA, GESTOR, ADMIN

**Complexidade**: 🟡 MÉDIA

**Estimativa**: 1-1,5 semanas

### 2.2) Funcionalidades Principais

#### F2.1 - KPI Cards
- 6 cards principais:
  * Total de Casos (+ variação %)
  * Total de Óbitos
  * Taxa de Letalidade
  * Incidência Média
  * Municípios Alto Risco
  * Casos Graves
- Design: coloridos, ícones, trends (↑↓→)
- Grid responsivo (1-4 colunas)

#### F2.2 - Séries Temporais
- Gráfico de linha (Chart.js)
- Agregações: semanal/mensal/anual
- Múltiplas séries sobrepostas
- Zoom/pan enabled
- Tooltip detalhado

#### F2.3 - Top N Municípios
- Gráfico de barras horizontais
- Indicadores: casos/incidência/óbitos
- Top 10 padrão (configurável 5-20)
- Cores por nível de risco
- Click para drill-down

#### F2.4 - Filtros
- Ano (2020-2026)
- Semanas epidemiológicas (range)
- Doença (DENGUE/ZIKA/CHIK/FA)
- Município (opcional)

#### F2.5 - Export
- CSV de datasets exibidos
- PNG dos gráficos
- PDF do dashboard completo (futuro)

### 2.3) Integrações Backend

**epi-api**:

```
GET /indicadores/kpis
GET /indicadores/series-temporais
GET /indicadores/top
```

### 2.4) Tecnologias

- React 18 + TS
- Chart.js + react-chartjs-2
- TailwindCSS
- lucide-react

### 2.5) Critérios de Aceite

✅ KPIs carregam em < 2s  
✅ Variações calculadas corretamente  
✅ Gráficos renderizam suavemente  
✅ Filtros funcionam sem delay  
✅ Export CSV completo  
✅ Responsivo (grid adaptativo)  
✅ Sem erros de console

---

## MÓDULO 3: ATIVIDADES DE CAMPO

### 3.1) Visão Geral

**Objetivo**: Gestão de atividades de campo (vistorias, LIRAa, nebulização, etc.)

**Público-Alvo**: CAMPO (CRUD próprio), VIGILANCIA/GESTOR (leitura), ADMIN (total)

**Complexidade**: 🟡 MÉDIA

**Estimativa**: 1,5 semanas

### 3.2) Funcionalidades Principais

#### F3.1 - Listagem de Atividades
- Tabela paginada (50/page)
- Colunas: tipo, status, município, data, responsável
- Filtros: status/tipo/município/período
- Ordenação por coluna
- Badge de status colorido

#### F3.2 - Detalhes da Atividade
- Informações completas
- Timeline de eventos
- Mapa com localização (pin)
- Lista de evidências anexadas
- Ações contextuais

#### F3.3 - Criar/Editar Atividade
- Formulário com validações
- Campos:
  * Tipo (select)
  * Município (autocomplete)
  * Localização (mapa picker)
  * Descrição
  * Metadata (JSON livre)
- Captura de GPS automática (PWA)

#### F3.4 - Transições de Estado
- CRIADA → EM_ANDAMENTO (auto-set iniciado_em)
- EM_ANDAMENTO → CONCLUIDA (auto-set encerrado_em)
- Qualquer → CANCELADA (apenas GESTOR/ADMIN)

#### F3.5 - Relatório de Atividade
- Sumário executivo
- Estatísticas (total/status/tipo)
- Export CSV

### 3.3) Integrações Backend

**campo-api** (http://localhost:8001/api):

```
GET    /atividades (list + pagination)
POST   /atividades (create)
GET    /atividades/{id} (detail)
PATCH  /atividades/{id} (update)
DELETE /atividades/{id} (soft delete)
GET    /atividades/stats/summary
```

### 3.4) Critérios de Aceite

✅ CRUD completo funcional  
✅ Transições de estado corretas  
✅ Validações impedem dados inválidos  
✅ GPS capture funciona (PWA)  
✅ Paginação eficiente  
✅ Filtros e ordenação funcionam

---

## MÓDULO 4: GESTÃO DE EVIDÊNCIAS

### 4.1) Visão Geral

**Objetivo**: Upload, visualização e gestão de evidências (fotos/vídeos/docs) vinculadas a atividades.

**Público-Alvo**: CAMPO (upload), todos (visualização)

**Complexidade**: 🟠 ALTA (PWA offline + S3)

**Estimativa**: 1,5-2 semanas

### 4.2) Funcionalidades Principais

#### F4.1 - Upload de Evidências
- Fluxo: presigned URL → upload direto S3 → register metadata
- Tipos suportados:
  * Foto: JPEG/PNG/WEBP (max 10MB)
  * Vídeo: MP4/MOV (max 50MB)
  * Documento: PDF (max 5MB)
  * Áudio: MP3/WAV (max 5MB)
- Preview antes de enviar
- Compressão automática de fotos
- Extração de EXIF (GPS, datetime, device)
- Watermark opcional

#### F4.2 - Galeria de Evidências
- Grid responsivo (2-6 colunas)
- Lightbox para visualização
- Filtro por tipo
- Download individual
- Delete (soft)

#### F4.3 - Offline Support (PWA)
- Fila de upload quando offline
- Background sync quando online
- Indicador de pendências
- Retry automático (max 3x)

#### F4.4 - Integridade
- Hash SHA-256 calculado no client
- Validação no server
- Merkle tree para conjuntos (relatório EVD01)

### 4.3) Integrações Backend

**campo-api**:

```
POST /atividades/{id}/evidencias/presigned-url
POST /atividades/{id}/evidencias
GET  /atividades/{id}/evidencias
DELETE /evidencias/{id}
```

**MinIO/S3**:
- Bucket: techdengue-evidencias
- Path: atividades/{id}/{uuid}_{filename}

### 4.4) Critérios de Aceite

✅ Upload direto S3 funcional  
✅ Preview antes de enviar  
✅ Compressão reduz tamanho em 30-50%  
✅ EXIF extraído corretamente  
✅ Fila offline persiste  
✅ Background sync funciona  
✅ Hash SHA-256 válido

---

## ANEXOS

### A) Stack Tecnológico Completo

**Frontend**:
- React 18.2
- TypeScript 5.x
- Vite 5.x
- TailwindCSS 3.x
- shadcn/ui
- React Router v6
- React Query (TanStack)
- Zustand
- Axios
- Leaflet + plugins
- Chart.js
- Lucide React
- oidc-client-ts

**Backend** (já implementado):
- FastAPI 0.108
- Python 3.11
- PostgreSQL 15 + TimescaleDB + PostGIS
- MinIO/S3
- Redis
- Celery
- Keycloak

**DevOps**:
- Docker + Compose
- GitHub Actions
- Netlify (frontend)
- Prometheus + Grafana
- Loki + Promtail

### B) Estimativas de Esforço

| Módulo | Complexidade | Estimativa | Devs |
|--------|--------------|------------|------|
| Mapa Vivo | ALTA | 2-3 semanas | 2 |
| Dashboard | MÉDIA | 1-1,5 semanas | 1 |
| Atividades | MÉDIA | 1,5 semanas | 1 |
| Evidências | ALTA | 1,5-2 semanas | 1 |
| Relatórios UI | BAIXA | 0,5 semana | 1 |
| ETL UI | BAIXA | 0,5 semana | 1 |
| Admin | MÉDIA | 1 semana | 1 |
| PWA Offline | ALTA | 1 semana | 1 |
| Testes E2E | MÉDIA | 1 semana | 1 |
| **TOTAL** | - | **9-12 semanas** | **1-2 devs** |

### C) Próximos Passos

1. ✅ Aprovação da Matriz de Implantação
2. ⏳ Sprint Planning (detalhamento de tarefas)
3. ⏳ Setup de ambiente de desenvolvimento
4. ⏳ Início da implementação (Mapa Vivo)

---

**FIM DO DOCUMENTO**
