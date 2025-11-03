# TechDengue MT — Status Técnico do Repositório

## 🎯 Objetivo deste documento

Consolidar, de forma prática e auditável, o mapeamento técnico do repositório, cobrindo:

- Visão geral e objetivos do desenvolvimento.
- Arquitetura e módulos (APIs, dados, observabilidade e CI/CD).
- Entregas executadas (por marco: M0, M1, M2, M3).
- Implementações pendentes e plano tático para conclusão.
- Referências cruzadas para arquivos e documentos existentes no repo.

> Fonte: análise direta da tree do repo, dos diretórios `campo-api`, `epi-api`, `relatorios-api`, `infra`, `db/flyway`, `.github/workflows` e dos documentos em `docs/`.

---

## 🧭 Visão geral do projeto

Plataforma de vigilância epidemiológica para o Estado de MT, com foco em:

- Coleta de campo (atividades, evidências) e geração de relatórios (Campo API).
- Indicadores epidemiológicos (ETL SINAN/LIRAa), mapa vivo e dashboards (EPI API).
- Observabilidade, automações e robustez operacional (jobs, métricas, alertas, logs).
- Entrega contínua e infraestrutura versionada (CI/CD + Docker Compose).

---

## 🗺️ Mapa de diretórios principais

- `campo-api/` — Backend de campo (atividades, evidências, relatórios).  
- `epi-api/` — Backend epidemiológico (ETL, indicadores, camadas de mapa).  
- `relatorios-api/` — Pipeline de relatórios (EPI01 e correlatos).  
- `frontend/` — Código do front (skeleton e recursos auxiliares).  
- `docs/` — Documentação técnica e operacional (roadmap, guias, validações).  
- `infra/` — Compose principal e stack de observabilidade (Prometheus, Grafana, Loki, Alertmanager, Promtail).  
- `db/flyway/migrations/` — Migrations SQL versionadas (V1…V11).  
- `.github/workflows/` — Pipelines de CI/CD (ci.yml, deploy.yml).

---

## 🏗️ Arquitetura (alto nível)

- Serviços backend (FastAPI):  
  - Campo API (coleta/evidências/relatórios)  
  - EPI API (ETL + indicadores + mapa)  
  - Relatórios API (relatórios epidemiológicos)
- Data Lake/DB: PostgreSQL (+ TimescaleDB, PostGIS).  
- Mensageria/Jobs: Celery + Redis.  
- Storage de arquivos: MinIO/S3.  
- Autenticação/Autorização: Keycloak (OIDC).  
- Observabilidade: Prometheus + Grafana + Loki + Promtail + Alertmanager.  
- Entrega: GitHub Actions CI/CD + Docker Compose.

---

## ✅ Entregas executadas (por marco)

### M0 — Fundações (Concluído)

- Estrutura de repositório, ambientes e automações iniciais.  
- Compose base, Postgres + extensões, Redis, MinIO, Keycloak.  
- OpenAPI inicial e organização de documentos base.  
- Documentos: `docs/1_Fundacoes.md`, `VALIDACAO_M0.md`, `OBSERVABILIDADE.md`.

### M2 — Campo API & Field MVP (Concluído)

- Rotas CRUD de atividades e gestão de evidências (upload + metadados).  
- Integrações S3/MinIO e extração EXIF; integridade de arquivos.  
- Relatório EVD01, com composição a partir de dados de campo.  
- Documentos: `docs/M2_README.md`, `docs/M2_API_REFERENCE.md`, `docs/M2_GUIA_INTEGRACAO.md`.

> Observação: Detalhes de endpoints, payloads e exemplos estão documentados nos arquivos acima; o repositório contém os módulos correspondentes dentro de `campo-api/`.

### M3 — Sync, Jobs, CI/CD e Observabilidade (Concluído)

- Rotina de jobs com Celery + Redis (tasks e agendamentos).  
- Pipelines de CI/CD (`.github/workflows/ci.yml`, `.github/workflows/deploy.yml`).  
- Stack de observabilidade (Prometheus, Grafana, Loki, Alertmanager, Promtail).  
  - Arquivos:  
    - `infra/docker-compose.monitoring.yml`  
    - `infra/monitoring/prometheus.yml`  
    - `infra/monitoring/alert_rules.yml`  
    - `infra/monitoring/alertmanager.yml`  
    - `infra/monitoring/loki-config.yml`  
    - `infra/monitoring/promtail-config.yml`  
    - `infra/monitoring/grafana/**` (datasources, dashboards)  
- Documentos: `docs/M3_README.md`, `docs/OBSERVABILIDADE.md`.

### M1 — Epidemiologia (em andamento)

- ETL EPI (SINAN + LIRAa) — Concluído:  
  - Schemas e validações (`epi-api/app/schemas/etl.py`).  
  - Services: `etl_base_service.py`, `sinan_etl_service.py`, `liraa_etl_service.py`.  
  - Rotas ETL: `epi-api/app/routers/etl.py` (import, job status/list).  
  - Tarefas Celery: `epi-api/app/tasks/etl_tasks.py`.  
  - Tabela de tracking: `db/flyway/migrations/V11__add_etl_jobs_table.sql`.  
  - Documentos: `docs/M1_ETL_README.md`, `docs/ETL_EPI_GUIA.md`.

- Backend Mapa (camadas e estatísticas) — Concluído:  
  - Schemas: `epi-api/app/schemas/mapa.py` (GeoJSON, heatmap, filtros, séries).  
  - Service: `epi-api/app/services/mapa_service.py` (incidência, heatmap, séries, stats).  
  - Rotas: `epi-api/app/routers/mapa.py` (camadas, heatmap, estatísticas, séries, municípios).  

- Documentos de acompanhamento: `docs/M1_PROGRESSO.md`, `docs/M1_RELATORIO_VALIDACAO.md`, `docs/M1_GUIA_COMPLETO.md`.

---

## 🧩 Estado das APIs (routers principais)

- EPI API  
  - ETL: `POST /api/etl/sinan/import`, `POST /api/etl/liraa/import`, `GET /api/etl/jobs/{id}`, `GET /api/etl/jobs`.  
  - Mapa: `GET /api/mapa/camadas`, `GET /api/mapa/heatmap`, `GET /api/mapa/estatisticas`, `GET /api/mapa/series-temporais/{codigo_ibge}`, `GET /api/mapa/municipios`.

- Campo API  
  - CRUD Atividades, Evidências e Relatórios de campo (ver `docs/M2_*`).

- Relatórios API  
  - Estruturada para relatórios EPI (p.ex., EPI01). Rotas/serviços a consolidar com M1.4.

> Dica: Detalhes de payload, autenticação e exemplos estão nos documentos `docs/M2_API_REFERENCE.md`, `docs/M2_GUIA_INTEGRACAO.md` e `docs/M1_ETL_README.md`.

---

## 🗃️ Banco de Dados — Migrations Flyway

- V1 — `create_extensions_and_enums.sql`  
- V2 — `create_tables.sql`  
- V3 — `create_indexes.sql`  
- V4 — `insert_seeds.sql`  
- V5 — `add_epi_columns.sql`  
- V6 — `make_old_columns_nullable.sql`  
- V7 — `add_dedup_key.sql`  
- V8 — `create_atividade_evidencia.sql`  
- V9 — `update_atividade_status_enum.sql`  
- V10 — `add_background_jobs_tables.sql`  
- V11 — `add_etl_jobs_table.sql`  

> Observação: os nomes são autoexplicativos; para detalhes de colunas/índices, consultar cada arquivo em `db/flyway/migrations/`.

---

## 🔭 Observabilidade & DevOps

- Compose de monitoramento: `infra/docker-compose.monitoring.yml`.  
- Prometheus (scrapes + alertas): `infra/monitoring/prometheus.yml`, `alert_rules.yml`.  
- Grafana (datasources + dashboards): `infra/monitoring/grafana/**`.  
- Logs centralizados (Loki + Promtail): `infra/monitoring/loki-config.yml`, `promtail-config.yml`.  
- Alertmanager: `infra/monitoring/alertmanager.yml`.  
- CI/CD: `.github/workflows/ci.yml`, `.github/workflows/deploy.yml`.

---

## 🔐 Segurança

- Autenticação via Keycloak (scripts e testes utilitários no repo: `test_keycloak.py`).  
- Boas práticas de validação nos schemas Pydantic e sanitização de entradas.  
- Observabilidade e alertas para detectar regressões e falhas operacionais.

---

## 🧪 Qualidade & Testes

- Testes utilitários e de integração:  
  - `test_db.py`, `test_keycloak.py`, `test_observability.py`, `test_prism.py`, `test_user_login.py`.  
- Caderno e guias de testes: `docs/CADERNO_DE_TESTES.md`, `docs/ANALISE_E_VALIDACAO.md`.

> Observação: Para M1 (ETL+Mapa), há conjunto dedicado em `epi-api/tests/` (validações de ETL, normalizações, leitura de CSV, cálculos de índices e séries).

---

## 📌 Implementações pendentes (priorizadas)

### 1) M1.3 — Dashboard EPI (KPIs + Gráficos)

- Endpoints (sugestão):  
  - `GET /api/indicadores/kpis` — Totais, variação, tendência.  
  - `GET /api/indicadores/series-temporais` — Séries por doença/município.  
  - `GET /api/indicadores/top` — Top N por incidência/casos.  
- Frontend: componentes de cards, gráficos (linhas/barras), drill-down por município.

### 2) M1.4 — Relatório EPI01 (PDF + CSV)

- Gerador no `relatorios-api/` (PDF/A-1, gráficos embarcados, hashes).  
- Endpoints (sugestão):  
  - `GET /api/relatorios/epi01` — geração sob demanda (filtros: período/município/doença).  
  - `GET /api/relatorios/epi01/download/{id}` — download + metadados.

### 3) Frontend React PWA (Mapa + Dash + Campo)

- Páginas: Login/Keycloak, Mapa Vivo (Leaflet), Dashboard EPI, Atividades/Evidências, Relatórios.  
- PWA: Service Worker, IndexedDB (fila de sync), Background Sync, Offline-first.  
- Integração com APIs existentes (mapa/etl/indicadores/campo).

### 4) Testes E2E e Performance

- E2E com Playwright/Cypress (fluxos críticos).  
- Performance (k6): latência p95 das rotas de mapa (≤ 4s) e ETL em lotes.  
- Observabilidade: painéis e alertas orientados a SLOs.

### 5) Hardening/Polish

- Segurança API (rate limit, headers, audit logs).  
- Lint de docs (markdownlint) e links verificados.  
- Rotas IPO/IDO/IVO/IMO (quando os datasets estiverem disponíveis).

---

## 📅 Plano tático (sugestão)

```text
Sprint A (1-2 semanas):
  - M1.3 Dashboard: endpoints + UI (MVP)
  - KPIs e séries + caching e paginação

Sprint B (1 semana):
  - M1.4 Relatório EPI01 end-to-end
  - Export PDF/CSV + hash + auditoria

Sprint C (2-3 semanas):
  - Frontend PWA (Service Worker, IndexedDB, Background Sync)
  - Integração completa com Mapa + ETL + KPIs

Sprint D (1 semana):
  - E2E + carga + observabilidade orientada a SLO
  - Bug bash e documentação final
```

---

## 🔗 Documentos-chave (referência rápida)

- Status/roadmap: `docs/PROJECT_STATUS.md`, `docs/ROADMAP_VISUAL.md`, `docs/ROADMAP.md`.  
- M1 (ETL, Mapa): `docs/M1_ETL_README.md`, `docs/M1_PROGRESSO.md`, `docs/M1_GUIA_COMPLETO.md`.  
- M2 (Campo): `docs/M2_README.md`, `docs/M2_API_REFERENCE.md`, `docs/M2_GUIA_INTEGRACAO.md`.  
- M3 (Infra/Obs): `docs/M3_README.md`, `docs/OBSERVABILIDADE.md`.  
- OpenAPI: `docs/openapi/README.md`.

---

## ✅ Conclusão (estado atual)

- M0, M2, M3 — Concluídos e documentados.  
- M1 — Em andamento; **ETL + backend de Mapa concluídos**; pendente Dashboard EPI (UI+APIs complementares) e Relatório EPI01.  
- Frontend PWA — Estrutura presente; features e integração por implementar.  
- Infra & Observabilidade — Provisionadas e versionadas; CI/CD presentes.

Este documento deve servir como fonte única de verdade para acompanhamento técnico. Atualizações recomendadas ao concluir cada subentrega (commits de docs acompanhando PRs).
