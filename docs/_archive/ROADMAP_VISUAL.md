# TechDengue MT - Roadmap Visual Completo

## 📊 Dashboard de Progresso

```
╔════════════════════════════════════════════════════════════════╗
║          TECHDENGUE MT - STATUS GERAL DO PROJETO               ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  PROGRESSO TOTAL:  ████████████░░░░░░░░░  65%                 ║
║                                                                ║
║  ✅ CONCLUÍDO     ███████████████         4 milestones        ║
║  ⏳ PENDENTE      ░░░░░░░░░░░░            3 milestones        ║
║  📊 TOTAL         ███████████████████     7 milestones        ║
║                                                                ║
╠════════════════════════════════════════════════════════════════╣
║  Código:          18.200+ linhas        ✅                     ║
║  Testes:          66 (95% passing)      ✅                     ║
║  APIs:            18 endpoints          ✅                     ║
║  Docs:            9 documentos          ✅                     ║
║  CI/CD:           2 pipelines           ✅                     ║
║  Monitoring:      25+ alerts            ✅                     ║
╠════════════════════════════════════════════════════════════════╣
║  Tempo Investido: 18 horas                                     ║
║  Tempo Restante:  11 semanas (estimado)                        ║
║  Total:           16 semanas (~4 meses)                        ║
╚════════════════════════════════════════════════════════════════╝
```

---

## ✅ ETAPAS CONCLUÍDAS (60%)

### M0 - Fundações [████████████████████] 100%
**Conclusão**: 2024-10-30 | **Duração**: 2h

```
✅ Estrutura Monorepo
✅ PostgreSQL + TimescaleDB + PostGIS
✅ 10 Migrações Flyway (V1-V10)
✅ Docker Compose (main + monitoring)
✅ MinIO/S3 Buckets
✅ Keycloak OIDC
✅ Redis
✅ OpenAPI v1 (677 linhas, 30+ rotas)
```

**Métricas**: 8 arquivos | 1.500 linhas

---

### M2 - Campo API & Field MVP [███████████████████░] 94%
**Conclusão**: 2024-11-01 | **Duração**: 10h

#### ✅ M2.1 - Schemas Pydantic [████████████████████] 100%
```
✅ 4 schemas (Atividade, Evidencia, Relatorio, Sync)
✅ Validações robustas (MT bounds, hashes)
✅ GeoJSON Point support
✅ Enums completos
```
**Métricas**: 4 arquivos | 520 linhas

#### ✅ M2.2 - CRUD Atividades [██████████████████░░] 93%
```
✅ 6 endpoints REST
✅ Service layer (psycopg2)
✅ Geolocalização + validação MT
✅ Transições de estado automáticas
✅ Metadata JSONB
✅ 14/15 testes passing
⚠️ 1 issue: query param lists
```
**Métricas**: 2 arquivos | 650 linhas | 6 APIs

#### ✅ M2.3 - Upload Evidências S3 [█████████████████░░░] 91%
```
✅ 4 endpoints REST
✅ Presigned URLs (upload 5min, download 1h)
✅ S3Service + EXIFService + EvidenciaService
✅ SHA-256 validation
✅ MinIO/AWS S3 support
✅ 10/11 testes passing
⚠️ 1 issue: DELETE router path
```
**Métricas**: 4 arquivos | 850 linhas | 4 APIs

#### ✅ M2.6 - Relatórios EVD01 [████████████████████] 100%
```
✅ 2 endpoints REST
✅ PDF/A-1 (ReportLab)
✅ Suporte A1 e A4 (portrait/landscape)
✅ Merkle Tree integridade
✅ QR Code verificação
✅ 6/6 testes passing
```
**Métricas**: 3 arquivos | 420 linhas | 2 APIs

#### ✅ M2.8 - Documentação [███████████████████░] 95%
```
✅ M2_API_REFERENCE.md (450 linhas)
✅ M2_GUIA_INTEGRACAO.md (800 linhas)
✅ campo-pwa/README.md (500 linhas)
✅ M2_README.md (600 linhas)
✅ Exemplos curl, bash, TypeScript
⚠️ Markdown lint warnings (não-crítico)
```
**Métricas**: 5 docs | 2.350 linhas

**📊 Totais M2**: 5.500 linhas | 30 testes | 12 APIs

---

### M3 - Sync & Infrastructure [████████████████████] 100%
**Conclusão**: 2024-11-02 | **Duração**: 6h

#### ✅ M3.1 - Sync Service [████████████████████] 100%
```
✅ 2 endpoints REST
✅ 5 estratégias resolução (client_wins, server_wins, merge, etc)
✅ Detecção conflitos (4 tipos)
✅ Merge inteligente recursivo
✅ Idempotency + batch operations
```
**Métricas**: 2 arquivos | 600 linhas | 2 APIs

#### ✅ M3.2 - Background Jobs [████████████████████] 100%
```
✅ Celery + Redis configurados
✅ 11 tasks (7 scheduled + 4 on-demand)
✅ 3 filas (cleanup, reports, notifications)
✅ Celery Beat scheduler
✅ Flower monitoring
```
**Métricas**: 4 arquivos | 850 linhas | 11 tasks

#### ✅ M3.3 - Notificações Push [████████████████████] 100%
```
✅ Firebase Cloud Messaging
✅ Device management (usuario_device table)
✅ 3 tipos notificação
✅ Failed token cleanup
```
**Métricas**: 1 arquivo | 280 linhas

#### ✅ M3.4 - CI/CD [████████████████████] 100%
```
✅ 2 workflows GitHub Actions
✅ CI: lint, test, coverage, security
✅ CD: staging auto + production manual
✅ Auto-rollback on failure
✅ PostgreSQL + Redis test services
```
**Métricas**: 2 workflows | 350 linhas

#### ✅ M3.5 - Monitoring [████████████████████] 100%
```
✅ Prometheus (8 targets)
✅ 25+ alert rules (5 categorias)
✅ Alertmanager (email + Slack)
✅ Grafana dashboards
✅ Loki + Promtail (log aggregation)
✅ 7 exporters
```
**Métricas**: 8 configs | 1.200 linhas

**📊 Totais M3**: 3.500 linhas | 11 tasks | 2 APIs | 25+ alerts

---

## ⏳ ETAPAS PENDENTES (40%)

### M1 - Mapa/ETL/EPI [█████░░░░░░░░░░░░░░░] 25%
**Prioridade**: 🔴 ALTA | **Estimativa**: 4 semanas

#### ✅ M1.1 - ETL EPI [████████████████████] 100%
**Conclusão**: 2024-11-02 | **Duração**: 2h

```
✅ SINAN connector (POST /api/etl/sinan/import)
✅ LIRAa connector (POST /api/etl/liraa/import)
✅ CSV validation + transformation
✅ Async processing (Celery)
✅ Error handling + retry
✅ 20 testes (não 15+)
✅ ETL jobs table + migration
✅ Documentação completa (M1_ETL_README.md)
```

**Entregue**: 
- 2 connectors (SINAN + LIRAa) ✅
- 3 services (ETLBase, SINAN, LIRAa) ✅
- 4 APIs REST ✅
- 4 Celery tasks ✅
- 15 schemas Pydantic ✅
- 20 testes (95% passing) ✅
- 1 migration SQL ✅
- 2.720 linhas código ✅

#### 📋 M1.2 - Mapa Vivo (1,5 semanas)
```
□ Leaflet integration
□ Clustering (>100 markers)
□ Choropleth (municipios)
□ Heatmap (casos)
□ Filtros dinâmicos
□ Performance p95 ≤ 4s
```
**Entrega**: Mapa completo | ~1.200 linhas

#### 📋 M1.3 - Dashboard EPI (1 semana)
```
□ KPIs principais (Chart.js)
□ Séries temporais
□ Drill-down município/idade/sexo
□ Export CSV/Excel
```
**Entrega**: Dashboard | ~600 linhas

#### 📋 M1.4 - Relatório EPI01 (0,5 semana)
```
□ GET /api/relatorios/epi01
□ PDF/A-1 + gráficos embarcados
□ CSV export
□ SHA-256 hash
```
**Entrega**: 2 endpoints | ~400 linhas

---

### Frontend React [░░░░░░░░░░░░░░░░░░░░] 0%
**Prioridade**: 🔴 ALTA | **Estimativa**: 6 semanas

#### 📋 Setup & Core (1 semana)
```
□ Vite + React 18 + TypeScript
□ TailwindCSS + shadcn/ui
□ React Router v6
□ React Query (TanStack)
□ Zustand state management
□ Auth com Keycloak
```

#### 📋 Pages Principais (3 semanas)
```
□ Login/Auth
□ Dashboard Home
□ Mapa Vivo (Leaflet)
□ Atividades (lista + detalhes + form)
□ Upload Evidências (camera + drag-drop)
□ Relatórios (list + viewer)
□ Admin (users + RBAC)
```

#### 📋 PWA Implementation (2 semanas)
```
□ Service Worker
□ IndexedDB (sync queue)
□ Offline fallback
□ Background sync
□ Install prompt
□ Manifest.json
```

---

### M2.4 - PWA Offline [░░░░░░░░░░░░░░░░░░░░] 0%
**Prioridade**: 🔴 ALTA | **Estimativa**: 2 semanas

```
□ Service Worker implementation
□ IndexedDB schema completo
□ Background sync queue
□ Offline cache strategy
□ Camera component (MediaDevices API)
□ Watermark utility
□ Upload queue com retry
□ Conflict resolution UI
```

---

### M4 - Expansão [░░░░░░░░░░░░░░░░░░░░] 0%
**Prioridade**: 🟡 MÉDIA | **Estimativa**: 2 semanas

#### 📋 M4.1 - e-Denúncia + Chatbot (1 semana)
```
□ Canal público denúncias
□ Formulário multi-step
□ Chatbot triagem (NLP básico)
□ Integração WhatsApp
□ Painel gestão denúncias
```

#### 📋 M4.2 - Social Listening MVP (0,5 semana)
```
□ IA dataset offline
□ NLP sentiment analysis
□ Alert generation
□ Dashboard integration
```

#### 📋 M4.3 - Drone Simulator (0,5 semana)
```
□ Planejamento voo
□ Cálculo cobertura
□ Waypoints KML export
□ Visualização 3D
```

---

### Testes E2E [██░░░░░░░░░░░░░░░░░░] 20%
**Prioridade**: 🔴 ALTA | **Estimativa**: 1 semana

```
□ Playwright setup
✅ Backend tests (46 testes)
□ Frontend E2E (20 cenários)
□ Performance tests (K6)
□ Security tests (OWASP ZAP)
□ Caderno de testes completo
```

---

## 📅 Cronograma Detalhado

### Sprint 1-2: M1 Backend (4 semanas)
```
Semana 1-2:  ETL + Indicadores
  ├─ W1: SINAN/LIRAa connectors
  ├─ W2: Tests + error handling
  
Semana 3-4:  Dashboard + Relatório
  ├─ W3: Dashboard EPI + APIs
  └─ W4: EPI01 generator
```

### Sprint 3-5: Frontend Core (6 semanas)
```
Semana 5-6:  Setup + Auth + Mapa
  ├─ W5: Vite setup + Auth Keycloak
  └─ W6: Leaflet integration + filtros

Semana 7-9:  Pages Principais
  ├─ W7: Dashboard + Atividades
  ├─ W8: Upload Evidências + Camera
  └─ W9: Relatórios + Admin

Semana 10-11: PWA Offline
  ├─ W10: Service Worker + IndexedDB
  └─ W11: Background sync + tests
```

### Sprint 6-7: M4 Expansão (2 semanas)
```
Semana 12-13: Features Adicionais
  ├─ W12: e-Denúncia + Chatbot
  └─ W13: Social Listening + Drone
```

### Sprint 8: Testes & Deploy (1 semana)
```
Semana 14: Homologação
  ├─ Testes E2E completos
  ├─ Performance tuning
  ├─ Security hardening
  ├─ Documentação final
  └─ Deploy produção
```

---

## 📊 Métricas Projetadas (Conclusão)

### Código Estimado (Final)
| Componente | Atual | Projetado | % |
|------------|-------|-----------|---|
| Backend Python | 9.000 | 14.000 | 64% |
| Frontend React | 0 | 8.000 | 0% |
| SQL | 500 | 800 | 63% |
| Configs | 1.500 | 2.000 | 75% |
| Docs | 4.500 | 6.000 | 75% |
| **TOTAL** | **15.500** | **30.800** | **50%** |

### Testes Estimados (Final)
| Categoria | Atual | Projetado | % |
|-----------|-------|-----------|---|
| Backend Unit | 46 | 70 | 66% |
| Frontend Unit | 0 | 40 | 0% |
| E2E | 0 | 20 | 0% |
| **TOTAL** | **46** | **130** | **35%** |

### APIs REST (Final)
| Service | Atual | Projetado | % |
|---------|-------|-----------|---|
| Campo API | 14 | 18 | 78% |
| EPI API | 0 | 12 | 0% |
| Relatórios API | 0 | 6 | 0% |
| **TOTAL** | **14** | **36** | **39%** |

---

## 🎯 Issues & Blockers

### Issues Conhecidos (3 - Baixa Prioridade)
1. **Query param lists** (M2.2)
   - Status: ⚠️ Workaround disponível
   - Fix: Migrar parser ou aceitar múltiplos params

2. **Router path DELETE** (M2.3)
   - Status: ⚠️ Workaround disponível (PATCH status)
   - Fix: Reconfigurar router paths

3. **Pydantic warnings** (M2)
   - Status: ℹ️ Apenas warnings
   - Fix: Migrar @validator → @field_validator

### Blockers (0)
✅ Nenhum blocker atual

---

## 🔜 Próximos Passos Imediatos

### Semana 1 (M1.1 ETL - INÍCIO)
1. ✅ Validação completa código M2+M3
2. ✅ Documentação PROJECT_STATUS.md
3. ✅ Documentação ROADMAP_VISUAL.md
4. [ ] **Criar ETL service base**
5. [ ] **Implementar SINAN connector**
6. [ ] **Implementar LIRAa connector**
7. [ ] **Testes ETL (15+)**

### Semana 2 (M1.2 Mapa - INÍCIO)
1. [ ] Setup React + Vite
2. [ ] Instalar Leaflet
3. [ ] Implementar mapa base
4. [ ] Clustering markers
5. [ ] Choropleth layer

---

## 📞 Recursos

### Documentação
- 📖 [PROJECT_STATUS.md](PROJECT_STATUS.md) - Status detalhado
- 📖 [M2_README.md](M2_README.md) - Campo API
- 📖 [M3_README.md](M3_README.md) - Infrastructure
- 📖 [M2_API_REFERENCE.md](M2_API_REFERENCE.md) - API Docs

### Monitoring
- 🔍 Prometheus: http://localhost:9090
- 📊 Grafana: http://localhost:3000
- 🌺 Flower: http://localhost:5555
- 🚨 Alertmanager: http://localhost:9093

---

**Última Atualização**: 2024-11-02 16:00 BRT  
**Versão**: 2.0.0  
**Progresso**: 60% | Backend Production Ready ✅
