# Roadmap — Edital-Core ++

## M0 — Fundações (Pré-dev)
**Objetivo:** base estável para construir sem retrabalho.

### Épicos
- E0.1 Arquitetura & Repositórios
- E0.2 Segurança & Identidade (OIDC/RBAC)
- E0.3 Dados & Storage (PostGIS/Timescale/S3)
- E0.4 Contratos (OpenAPI v1) & Mock
- E0.5 Observabilidade mínima

### Issues
- [ ] M0-01 Setup mono-repo (`frontend/`, `epi-api/`, `campo-api/`, `relatorios-api/`, `infra/`)
- [ ] M0-02 CI/CD (build/test/lint/scan/deploy) + canário
- [ ] M0-03 OIDC + RBAC (escopos: epi.*, campo.*, admin.*)
- [ ] M0-04 PostGIS+Timescale (Liquibase/Flyway) + seeds mínimos
- [ ] M0-05 Buckets S3: `etl/`, `evidencias/`, `relatorios/` (versionamento, KMS)
- [ ] M0-06 OpenAPI v1 + mock server
- [ ] M0-07 Logs estruturados + `X-Request-Id` + p95/p99 por rota

**Saída:** Login SSO ok em homolog, DB/S3 prontos, OpenAPI v1 publicado.

---

## M1 — Mapa Vivo, ETL EPI e Relatório EPI01
**Objetivo:** vigilância operacional e visível.

### Épicos
- E1.1 Mapa & Camadas (Inc/100k, IPO/IDO/IVO/IMO)
- E1.2 ETL EPI (upload, validação, qualidade)
- E1.3 Relatório EPI01 (PDF/CSV)

### Issues
- [ ] M1-01 Página “Mapa” (camadas, paleta, filtros)
- [ ] M1-02 `POST /v1/etl/epi/upload` + relatório de qualidade
- [ ] M1-03 Dashboard EPI (cartões KPI + tendência)
- [ ] M1-04 Relatório EPI01 PDF/A-1 + CSV (hash no rodapé)
- [ ] M1-05 `/datasets/catalog.json` (versões + checksums)

**Saída:** ETL validando, mapas até 10k feições p95 ≤ 4s, EPI01 baixável.

---

## M2 — Campo (MVP robusto) + EVD01
**Objetivo:** execução de campo com prova técnica.

### Épicos
- E2.1 Atividades (criar/atribuir/SLA)
- E2.2 PWA offline-first (IndexedDB + fila de sync)
- E2.3 Checklists, mídia geotag, insumos
- E2.4 Pacote de evidência + Relatório EVD01

### Issues
- [ ] M2-01 CRUD Atividades + agenda por equipe
- [ ] M2-02 PWA: fila de sync (rede intermitente)
- [ ] M2-03 Captura mídia (geotag, watermark, hash | Merkle root)
- [ ] M2-04 Baixa de insumos (lote/validade; bloquear vencidos)
- [ ] M2-05 EVD01 PDF/A-1 com miniaturas e metadados

**Saída:** 100% atividades encerráveis com evidência válida; EVD01 emitido.

---

## M3 — Operação & Admin; Exports Geo; Observabilidade/DLP
**Objetivo:** operar, medir e governar.

### Épicos
- E3.1 Painel Operacional (SLA/Prod/Pend)
- E3.2 Exports GeoJSON (RBAC/DLP)
- E3.3 Admin (usuários/territórios/parâmetros)
- E3.4 Observabilidade (NOC) + DLP

### Issues
- [ ] M3-01 Painel Operacional + CSV-OP01
- [ ] M3-02 `GET /v1/exports/atividades.geojson` (rate-limit + escopos)
- [ ] M3-03 Admin básico
- [ ] M3-04 Dash NOC (p95, error rate, filas) + alertas
- [ ] M3-05 DLP/mascara em exports

**Saída:** Painel entrega KPIs, exports obedecem RBAC/DLP, alertas ativos.

---

## M4 — Preparação p/ expansão + Homologação
**Objetivo:** compliance total ao edital e base plugável (SIVEPI/Drone/IA).

### Épicos
- E4.1 Stubs `/analytics`, `/rotas`, `/voo` (501) + OpenAPI
- E4.2 Tiles/COG/WMTS operacional (infra)
- E4.3 Webhooks & Catálogo de eventos
- E4.4 Homologação (caderno de testes)
- E4.5 Anexos do dossiê (Plano, Cronograma Físico-Financeiro, LGPD, Equipe, Requisitos)

### Issues
- [ ] M4-01 Stubs + contratos publicados
- [ ] M4-02 Tileserver + camada simples servida
- [ ] M4-03 Webhooks (atividade criada/fechada, ETL ok)
- [ ] M4-04 Caderno de testes (prints/logs)
- [ ] M4-05 Dossiê final (DOCX/PDF)

**Saída:** Dossiê aprovado; sistema demonstrável item-a-item do edital.

---

## Definição de Pronto (DoD)
- OpenAPI atualizado, testes de contrato, acessibilidade AA, logs estruturados, RBAC/DLP nas rotas de export, PDFs em PDF/A-1 com hash, exemplos (curl/Postman) em `/docs`.

