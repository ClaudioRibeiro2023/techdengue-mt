# Análise Profunda e Validação — TechDengue (Repositório + Plano)

Data: 2025-11-01  
Revisor: Análise técnica automatizada

---

## 1. Estado atual do repositório

### 1.1 Estrutura física

```text
/Techdengue_MT
  /docs/                              ✅ ÚNICO ARTEFATO PRESENTE
    1_Fundacoes.md                    ✅ Guia técnico M0-M4 (395 linhas)
    ROADMAP.md                        ✅ Backlog estruturado por marcos
    ETAPA_1_Banco_de_Dados.txt        ✅ DDL + Flyway + docker-compose
    CADERNO_DE_TESTES.md              ✅ Template criado (novo)
    PLANO_DE_IMPLEMENTACAO.md         ✅ Plano sênior criado (novo)
    openapi-v1.yaml.txt               ⚠️  DUPLICADO (a arquivar)
    /openapi/                         ✅ Fonte da verdade
      openapi-v1.yaml                 ✅ Contrato v1 (331 linhas)
      README.md                       ✅ Atualizado (fonte da verdade declarada)
      curl.sh, httpie.http            ✅ Exemplos de uso
    /pwa_offline/                     ✅ Skeleton técnico (SW, IndexedDB, sync)
    /report_pipiline/ [typo]          ⚠️  Renomear para report_pipeline
    /templates/                       ✅ DOCX (EPI01, EVD01, OP01)
    /windsurf_skeleton/               ✅ Esqueleto React+Tailwind (24 itens)
```

- **Ausentes**: código backend, frontend funcional, infra (IaC), DB físico, CI/CD.
- **Status**: **Repositório em fase de planejamento** (apenas docs).

### 1.2 Contexto de negócio

- **Domínio**: vigilância epidemiológica (dengue) em Minas Gerais/Brasil.
- **Finalidade**: responder a um **edital público** ("Edital-Core++") com compliance total.
- **Escopo técnico**:
  - **EPI**: ETL de indicadores (incidência/100k, IPO/IDO/IVO/IMO), mapas choropleth, relatórios EPI01 (PDF/A-1 + CSV).
  - **Campo**: PWA offline-first, captura de mídias georreferenciadas com watermark/hash, relatórios EVD01 (PDF/A-1).
  - **Operação**: painel SLA/KPI, admin (usuários/RBAC), exports GeoJSON com DLP.
  - **Expansão (stubs)**: analytics (forecast), rotas (otimização), drone (missões).
- **Requisitos não funcionais críticos**:
  - Offline-first resiliente (rede intermitente em campo).
  - Performance: p95 ≤ 4s em mapas (≤10k feições).
  - Segurança: OIDC/RBAC, DLP, auditoria, hash de evidências e relatórios.
  - Observabilidade: logs estruturados, métricas, tracing, alertas.
  - Compliance: PDF/A-1, caderno de testes por requisito, dossiê final.

---

## 2. Validação: Objetivos × Documentação × Plano

### 2.1 Alinhamento com 1_Fundacoes.md

| Tópico (Fundações) | Plano de Implementação | Status |
|---|---|---|
| Estrutura monorepo (frontend/epi-api/campo-api/relatorios-api/infra/openapi/db/docs) | ✅ Seção 2.1 idêntica | ✅ ALINHADO |
| Variáveis de ambiente (OIDC, DB, S3, MAP_TOKEN, JWT) | ✅ Seção 2.4 cobre | ✅ ALINHADO |
| DDL (auth_usuario, audit_log, indicador_epi, atividade, evidencia, insumo_mov) | ✅ Referenciado em 2.7 (Flyway V1..V4) | ✅ ALINHADO |
| Buckets S3 (etl/evidencias/relatorios) + versionamento + KMS | ✅ M0 entregáveis + ADR-002 | ✅ ALINHADO |
| OpenAPI v1 + mock (Prism) | ✅ M0 + seção 2.8 | ✅ ALINHADO |
| Observabilidade (logs JSON, X-Request-Id, p95, alertas) | ✅ M0 + seção 2.5 | ✅ ALINHADO |
| ETL EPI (CSV-EPI01, validação, qualidade, carga) | ✅ M1 + seção 3.1 | ✅ ALINHADO |
| Mapa (choropleth, cluster, p95 ≤ 4s) | ✅ M1 + seção 3.2 | ✅ ALINHADO |
| EPI01 (PDF/A-1 + CSV + hash) | ✅ M1 + seção 3.4 | ✅ ALINHADO |
| PWA offline (IndexedDB + fila de sync idempotente) | ✅ M2 + ADR-003 + seção 3.3 | ✅ ALINHADO |
| Evidências (geotag, watermark, SHA-256, Merkle root) | ✅ M2 + seção 3.3 | ✅ ALINHADO |
| EVD01 (PDF/A-1 + miniaturas + root hash) | ✅ M2 + seção 3.4 | ✅ ALINHADO |
| Painel operacional (SLA/Prod/Pend) | ✅ M3 | ✅ ALINHADO |
| Exports GeoJSON + RBAC/DLP | ✅ M3 + seção 3.5 | ✅ ALINHADO |
| Admin (usuários/escopos) | ✅ M3 | ✅ ALINHADO |
| Stubs 501 (/analytics, /rotas, /voo) | ✅ M4 | ✅ ALINHADO |
| Tiles/COG/WMTS | ✅ M4 | ✅ ALINHADO |
| Webhooks + catálogo de eventos | ✅ M4 | ✅ ALINHADO |
| Caderno de testes por requisito | ✅ M4 + referência a CADERNO_DE_TESTES.md | ✅ ALINHADO |
| Dossiê final (plano, cronograma, LGPD, equipe, requisitos) | ✅ M4 | ✅ ALINHADO |

**Resultado**: 100% dos itens de 1_Fundacoes.md estão cobertos no plano.

### 2.2 Alinhamento com ROADMAP.md

| Marco (Roadmap) | Plano de Implementação | Status |
|---|---|---|
| M0 — Fundações (7 issues) | ✅ M0 + seção 2 (governança) | ✅ ALINHADO |
| M1 — Mapa/ETL/EPI01 (5 issues) | ✅ M1 + seções 3.1, 3.2, 3.4 | ✅ ALINHADO |
| M2 — Campo/EVD01 (5 issues) | ✅ M2 + seções 3.3, 3.4 | ✅ ALINHADO |
| M3 — Operação/Admin/DLP (5 issues) | ✅ M3 + seções 3.5 | ✅ ALINHADO |
| M4 — Expansão/Homolog (5 issues) | ✅ M4 | ✅ ALINHADO |
| DoD (OpenAPI, testes contrato, a11y, logs, RBAC/DLP, PDFs hash, exemplos) | ✅ Seções 2.6 (testes), 2.8 (OpenAPI), 2.5 (logs), 3.4 (hash), 3.5 (DLP) | ✅ ALINHADO |

**Resultado**: 100% dos marcos e DoD cobertos.

### 2.3 Alinhamento com OpenAPI v1

| Rota (OpenAPI) | Plano de Implementação | Status |
|---|---|---|
| POST /etl/epi/upload | ✅ M1 + seção 3.1 | ✅ ALINHADO |
| GET /etl/epi/qualidade/{carga_id} | ✅ M1 + seção 3.1 | ✅ ALINHADO |
| GET /indicadores | ✅ M1 + seção 3.1 | ✅ ALINHADO |
| POST/GET /atividades | ✅ M2 + seção 3.3 | ✅ ALINHADO |
| PATCH /atividades/{id} | ✅ M2 + seção 3.3 | ✅ ALINHADO |
| POST/GET /atividades/{id}/evidencias | ✅ M2 + seção 3.3 | ✅ ALINHADO |
| GET /relatorios/epi01 | ✅ M1 + seção 3.4 | ✅ ALINHADO |
| GET /relatorios/evd01 | ✅ M2 + seção 3.4 | ✅ ALINHADO |
| GET /exports/atividades.geojson | ✅ M3 + seção 3.5 | ✅ ALINHADO |
| GET /analytics/forecast (stub 501) | ✅ M4 | ✅ ALINHADO |
| GET /rotas/sugestoes (stub 501) | ✅ M4 | ✅ ALINHADO |
| POST /voo/missoes (stub 501) | ✅ M4 | ✅ ALINHADO |

**Resultado**: 100% das rotas mapeadas no plano.

### 2.4 Validação técnica dos ADRs

| ADR | Adequação | Observações |
|---|---|---|
| ADR-001 Backend (NestJS/FastAPI) | ✅ ADEQUADO | Ambos suportam PostGIS (via ORM), OpenAPI nativo, TS/Python são skills comuns |
| ADR-002 S3 (minio/cloud + versionamento + SSE-KMS) | ✅ ADEQUADO | Essencial para evidências e relatórios; versionamento protege contra deleção acidental |
| ADR-003 PWA offline-first (SW + IndexedDB + sync idempotente) | ✅ ADEQUADO | Crítico para campo (rede instável); idempotência previne duplicações |
| ADR-004 Observabilidade (OTel + Prom + Loki/ELK + X-Request-Id) | ✅ ADEQUADO | Stack moderna e interoperável; correlação end-to-end via X-Request-Id |
| ADR-005 Gateway/API (rate limit + DLP + CORS + headers) | ✅ ADEQUADO | Segurança em camadas; DLP essencial para compliance (edital/LGPD) |

**Resultado**: 5/5 ADRs adequados e bem fundamentados.

---

## 3. Gaps e riscos identificados

### 3.1 Gaps no plano

| Gap | Severidade | Recomendação |
|---|---|---|
| **Definição de stack backend** (NestJS vs FastAPI) pendente | 🟡 MÉDIA | Decidir em Sprint 1 (M0); sugestão: FastAPI (menor curva, PostGIS via GeoAlchemy2, OpenAPI nativo) |
| **Ferramenta de PDF/A-1** não especificada | 🟡 MÉDIA | Validar opções: LibreOffice headless, WeasyPrint, Puppeteer + pdf-lib. Testar conformidade A-1 em M1. |
| **Estratégia de resolução de conflitos offline** (apenas "LWW" citado) | 🟡 MÉDIA | Detalhar em ADR-003: LWW por `updated_at` servidor + telemetria de conflitos rejeitados. |
| **Política de retenção de logs/auditoria** não definida | 🟢 BAIXA | Adicionar em seção 2.5: 90d quente, >90d S3 ou archive, purge após 1 ano (LGPD). |
| **Plano de DR (Disaster Recovery) e backups** ausente | 🟡 MÉDIA | Adicionar em seção 4: backups DB (diário + retenção 30d), S3 replicação cross-region, RTO/RPO objetivos. |
| **Gestão de feature flags e rollout canário** mencionada mas não detalhada | 🟢 BAIXA | Adicionar ferramenta sugerida (LaunchDarkly, Unleash, ou simples via DB + cache). |
| **Definição de SLOs por rota crítica** não quantificada | 🟡 MÉDIA | Adicionar tabela em seção 2.5: p95 ≤ 500ms (indicadores), ≤ 4s (mapa), ≤ 2s (upload presigned), error rate ≤ 1%. |

### 3.2 Riscos técnicos

| Risco | Probabilidade | Impacto | Mitigação (adicional) |
|---|---|---|---|
| **OIDC/IdP fora do controle** (atraso provisionamento) | 🟡 MÉDIA | 🔴 ALTO | Mock OIDC (Keycloak local) desde Sprint 1; plano B: autenticação básica temporária (apenas homolog). |
| **Performance de mapas com >10k feições** | 🟢 BAIXA | 🟡 MÉDIO | Já mitigado: materializações, tiles, limites. Adicionar: server-side clustering (Supercluster). |
| **Sincronização offline com dados grandes** (vídeos) | 🟡 MÉDIA | 🔴 ALTO | Adicionar: compressão (H.264), chunked upload com retomada, limite de tamanho (ex: 50MB/vídeo). |
| **Conformidade PDF/A-1 não verificável automaticamente** | 🟡 MÉDIA | 🟡 MÉDIO | Adicionar: validação com veraPDF no CI; testes de conformidade por relatório. |
| **Carga de ETL com arquivos grandes** (>50MB CSV) | 🟢 BAIXA | 🟡 MÉDIO | Adicionar: streaming parser (csv-parse), validação por chunks, timeout configurável. |
| **Lock de tabelas durante migrações Flyway** | 🟢 BAIXA | 🟡 MÉDIO | Adicionar: janelas de manutenção, migrações online (quando possível), testes em clone. |

### 3.3 Gaps organizacionais

| Gap | Severidade | Recomendação |
|---|---|---|
| **Papéis e responsabilidades** (Code Owners) não definidos | 🟡 MÉDIA | Adicionar CODEOWNERS por módulo (frontend/epi-api/campo-api/infra/docs). |
| **Política de secrets e rotação** não documentada | 🟡 MÉDIA | Adicionar em seção 2.4: vault obrigatório, rotação 90d, sem segredos em env vars plaintext. |
| **Processo de deploy em produção** (aprovações) não detalhado | 🟡 MÉDIA | Adicionar em seção 4: aprovação PO + 2 devs, janela (terças/quintas 10h-16h), rollback automático se error rate > 5%. |
| **Plano de comunicação com stakeholders** ausente | 🟢 BAIXA | Adicionar: demos por sprint (M1-M4), reports semanais, Slack/email para incidentes. |

---

## 4. Consistência interna dos documentos

### 4.1 Nomenclatura e termos

| Termo | Uso em 1_Fundacoes.md | Uso em ROADMAP.md | Uso em PLANO_DE_IMPLEMENTACAO.md | Status |
|---|---|---|---|---|
| "Edital-Core++" | ✅ Mencionado | ✅ Título | ✅ Contexto OpenAPI | ✅ CONSISTENTE |
| Marcos (M0-M4) | ✅ Estrutura | ✅ Estrutura | ✅ Estrutura | ✅ CONSISTENTE |
| OpenAPI v1 | ✅ Seção 0.6 | ✅ Issue M0-06 | ✅ Seção 2.8 | ✅ CONSISTENTE |
| Flyway (migrações) | ✅ Seção 0.3 | ✅ Issue M0-04 | ✅ Seção 2.7 | ✅ CONSISTENTE |
| PDF/A-1 + hash | ✅ Seções 1.3, 2.4 | ✅ Issues M1-04, M2-05 | ✅ Seção 3.4 | ✅ CONSISTENTE |
| RBAC escopos | ✅ Papéis (GESTOR/VIGILANCIA/CAMPO/ADMIN) | ✅ Issue M0-03 | ✅ Seção 2.4 | ⚠️  INCONSISTÊNCIA LEVE (papéis vs escopos OAuth) |
| Performance (p95 ≤ 4s) | ✅ Seção 1.2 | ✅ Issue M1-01 | ✅ M1 critérios | ✅ CONSISTENTE |

**Inconsistência identificada**: `1_Fundacoes.md` usa papéis (GESTOR/VIGILANCIA/CAMPO/ADMIN) na tabela `auth_usuario`, mas ROADMAP e Plano citam escopos OAuth (`epi.*`, `campo.*`, `admin`). **Recomendação**: alinhar mapeamento papel → escopos em ADR ou seção de segurança.

### 4.2 Estrutura de pastas

| Pasta proposta (1_Fundacoes.md) | Plano (seção 2.1) | Status |
|---|---|---|
| /frontend | ✅ Idêntico | ✅ CONSISTENTE |
| /epi-api | ✅ Idêntico | ✅ CONSISTENTE |
| /campo-api | ✅ Idêntico | ✅ CONSISTENTE |
| /relatorios-api | ✅ Idêntico | ✅ CONSISTENTE |
| /infra | ✅ Idêntico | ✅ CONSISTENTE |
| /openapi | ✅ Idêntico | ✅ CONSISTENTE |
| /docs | ✅ Idêntico | ✅ CONSISTENTE |
| /db/migrations | ✅ /db/flyway (variação aceitável) | ✅ CONSISTENTE |

**Resultado**: 100% consistente.

---

## 5. Validação de viabilidade técnica

### 5.1 Tecnologias propostas (factibilidade)

| Stack | Adequação | Observações |
|---|---|---|
| **Backend**: NestJS ou FastAPI | ✅ VIÁVEL | NestJS: TS, modular, TypeORM; FastAPI: Python, rápido, Pydantic. Ambos produção-ready. |
| **DB**: PostgreSQL + PostGIS + Timescale | ✅ VIÁVEL | Stack madura; Timescale para séries temporais (competências); PostGIS para geo. |
| **Migrações**: Flyway | ✅ VIÁVEL | Robusto, versionamento, rollback; alternativa: Liquibase (mais verboso). |
| **Frontend**: React + Tailwind | ✅ VIÁVEL | Windsurf skeleton já existe; comunidade ativa; PWA suportada. |
| **PWA**: Service Worker + IndexedDB | ✅ VIÁVEL | Padrão web; libs: Workbox, Dexie.js. |
| **Mapas**: Leaflet ou MapLibre | ✅ VIÁVEL | Ambas abertas; MapLibre para tiles vetoriais; Leaflet mais simples. |
| **S3**: MinIO ou cloud (AWS/GCS/Azure) | ✅ VIÁVEL | MinIO para on-premise; cloud para escala. |
| **Observabilidade**: OTel + Prom + Loki | ✅ VIÁVEL | Stack CNCF; integrações prontas; alternativa: ELK. |
| **CI/CD**: GitHub Actions, GitLab CI, Azure DevOps | ✅ VIÁVEL (não especificado) | Adicionar escolha em seção 4. |
| **IaC**: Terraform + Helm/K8s | ✅ VIÁVEL | Terraform multi-cloud; K8s para orquestração; alternativa: Docker Compose (dev). |

**Resultado**: 100% das tecnologias são viáveis e maduras.

### 5.2 Estimativas de esforço (cronograma)

| Sprint | Duração | Escopo (Plano) | Viabilidade | Observações |
|---|---|---|---|---|
| S1-S2 (M0) | 4 semanas | Monorepo, CI/CD, DB, S3, OIDC, obs | ⚠️  APERTADO | 2 devs full-time; priorizar mock OIDC e DB local. |
| S3-S4 (M1) | 4 semanas | ETL, mapa, EPI01 | ✅ VIÁVEL | ETL direto; mapa com libs prontas. |
| S5-S6 (M2) | 4 semanas | PWA, evidências, EVD01 | ⚠️  APERTADO | Sync offline é complexo; alocar 1 dev especialista PWA. |
| S7 (M3) | 2 semanas | Operacional, Admin, DLP | ✅ VIÁVEL | Reutiliza RBAC de M0. |
| S8 (M4) | 2 semanas | Stubs, tiles, testes, dossiê | ⚠️  APERTADO | Caderno de testes demanda tempo; iniciar desde M1. |

**Recomendação**: realocar 1 semana de M3 para M2 (PWA) e iniciar caderno de testes em paralelo desde M1.

---

## 6. Prioridades de ajuste no plano

### 6.1 Ajustes obrigatórios (antes de M0)

1. **Decidir stack backend** (NestJS vs FastAPI) → sugestão: FastAPI (simplicidade, PostGIS via GeoAlchemy2).
2. **Alinhar papéis (DB) com escopos OAuth** → criar tabela de mapeamento em seção 2.4.
3. **Definir ferramenta PDF/A-1** → validar WeasyPrint ou LibreOffice headless + veraPDF.
4. **Adicionar SLOs quantitativos** por rota crítica (tabela em seção 2.5).
5. **Detalhar estratégia de conflitos offline** (LWW + telemetria) em ADR-003.

### 6.2 Ajustes recomendados (antes de M1)

6. **Adicionar plano de DR/backups** (seção 4).
7. **Documentar gestão de secrets e rotação** (seção 2.4).
8. **Definir ferramenta de feature flags** (LaunchDarkly/Unleash ou DB simples).
9. **Adicionar política de retenção de logs** (seção 2.5).
10. **Criar CODEOWNERS** por módulo (frontend/backend/infra/docs).

### 6.3 Melhorias futuras (M2+)

11. **Adicionar testes de carga** (k6 ou Locust) em seção 2.6.
12. **Documentar processo de deploy produção** (aprovações, janelas) em seção 4.
13. **Adicionar ERD do schema** (PlantUML ou Mermaid) em `docs/db_erd.md`.
14. **Plano de comunicação** com stakeholders (demos, reports).

---

## 7. Pontos fortes do plano

1. ✅ **Alinhamento total** com documentos de referência (1_Fundacoes.md, ROADMAP.md, OpenAPI v1).
2. ✅ **Abordagem sênior**: ADRs, observabilidade desde M0, contratos primeiro, segurança by design.
3. ✅ **Faseamento claro** (M0-M4) com critérios de saída objetivos e testáveis.
4. ✅ **Governança bem estruturada**: branching, commits, testes (pirâmide), scans, qualidade.
5. ✅ **Compliance desde o design**: RBAC/DLP, PDF/A-1 + hash, auditoria, caderno de testes.
6. ✅ **Riscos identificados** e mitigações propostas (mocks, materializações, idempotência).
7. ✅ **Stack técnico moderno e viável**: PostGIS, Timescale, OTel, IaC, PWA offline-first.

---

## 8. Recomendação final

### Status geral: ✅ **PLANO VALIDADO** (com ajustes menores)

- **Cobertura**: 100% dos requisitos de 1_Fundacoes.md e ROADMAP.md mapeados.
- **Viabilidade técnica**: 100% das tecnologias são maduras e produção-ready.
- **Gaps críticos**: nenhum (apenas refinamentos).
- **Prioridade imediata**: executar ajustes obrigatórios (seção 6.1) antes de iniciar M0.

### Próximos passos sugeridos

1. **Aplicar ajustes obrigatórios** (1-5 da seção 6.1) no `PLANO_DE_IMPLEMENTACAO.md`.
2. **Renomear pasta** `report_pipiline` → `report_pipeline`.
3. **Arquivar** `openapi-v1.yaml.txt` duplicado.
4. **Criar pastas base do monorepo** conforme seção 2.1 do plano.
5. **Iniciar M0 Sprint 1**: setup CI/CD + docker-compose DB + Flyway V1..V4 + OpenAPI lint.

---

**Validação técnica completa. Plano aprovado para execução.**
