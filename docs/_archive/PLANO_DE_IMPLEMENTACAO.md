# Plano de Implementação — TechDengue (Nível Sênior)

## 0. Objetivo e princípios

- Entregar uma base sólida e sustentável, com contratos estáveis, segurança por padrão e operabilidade desde o dia 1.
- Princípios: simplicidade intencional, contratos primeiro (OpenAPI), segurança by design, observabilidade end-to-end, automação máxima, compatibilidade progressiva.

## 1. Fases macro (P, M0–M4)

### Fase P — Prova de Conceito (PoC Pré-adjudicação)

- **Objetivo**: Demonstrar solução tecnológica aderente às especificações do TR (ANEXO I) do edital CINCOP/MT Pregão 014/2025.
- **Natureza**: Obrigatória e eliminatória (art. 17, § 3º e art. 41, II, Lei 14.133/2021).
- **Entregáveis PoC**:
  - Plataforma web com georreferenciamento, relatórios e dashboards.
  - Aplicativo móvel com chatbot, canal de denúncia e integração vigilância.
  - Sistema IA (Social Listening simulado com dataset offline).
  - Demonstração de integração SINAN/LIRAa (conectores PoC com CSV exemplo).
  - Simulação de plano de voo e operação VANTs (drones) com dispersão de larvicidas.
  - Controle de acesso, trilha de auditoria e segurança (OIDC, RBAC, audit_log).
  - Geração/visualização de relatórios com filtros e exportação (EPI01/EVD01/GeoJSON).
- **Prazo**: Notificação 48h antes; apresentação presencial com equipamentos pela licitante.
- **Avaliação**: Comissão técnica com checklist, eliminatória se não atender critérios.
- **Artefatos**:
  - Catálogo/prospecto/ficha técnica dos módulos.
  - Datasets de demonstração (indicadores EPI, atividades, evidências).
  - Roteiro de casos de teste e checklist de validação (vide `docs/POC_CHECKLIST.md`).
  - Laudo de Aceitabilidade emitido pela comissão.
- **Critérios de saída**:
  - Demonstração aprovada pela comissão técnica.
  - Laudo de Aceitabilidade emitido.
  - Proposta aceita e habilitada para adjudicação.

---

### M0 — Fundações (Pré-dev)

- Entregáveis
  - Monorepo estruturado e pipelines CI/CD mínimos.
  - OpenAPI v1 publicado e mockável.
  - Banco Timescale/PostGIS provisionado com migrações (Flyway) e seeds.
  - Buckets S3 (etl/evidencias/relatorios) com versionamento e SSE.
  - OIDC (homolog) e RBAC básico por escopos.
  - Observabilidade mínima (logs JSON, métricas por rota, tracing básico).
- Tópicos chave (detalhes na seção 2)
  - Estrutura de pastas, padrões de código/commit, revisão e ADRs.
  - Pipelines: lint, test, build, scan (SAST/deps), deploy canário.
  - Gestão de segredos e configuração por ambiente.
- Critérios de saída (DoD)
  - OpenAPI validado (lint) e acessível via Swagger UI e Prism.
  - DB sobe com `docker-compose`, `flyway migrate` aplica `V1..V4`.
  - `X-Request-Id` propagado; métricas p95 por rota expostas.
  - Login SSO funcionando em homolog.

### M1 — Mapa Vivo, ETL EPI e Relatório EPI01

- Entregáveis
  - Upload ETL EPI com validação e relatório de qualidade.
  - Camadas de mapa (incidência/100k, IPO/IDO/IVO/IMO) com performance (≤10k feições, p95 ≤ 4s).
  - Relatório EPI01 PDF/A-1 + CSV com hash no rodapé.
- Critérios de saída
  - Contratos e exemplos (curl/httpie) atualizados.
  - KPIs de ETL e mapa no dashboard NOC básico.

### M2 — Campo (MVP robusto) + EVD01

- Entregáveis
  - PWA offline-first (IndexedDB + fila de sincronização idempotente).
  - Captura de mídia com geotag, watermark e hash; upload por presigned URL.
  - EVD01 PDF/A-1 com miniaturas e root hash (Merkle) por atividade.
- Critérios de saída
  - Fluxos offline → online resilientes com retries e resolução de conflitos.
  - 100% atividades encerráveis com evidência válida.

### M3 — Operação & Admin; Exports Geo; Observabilidade/DLP

- Entregáveis
  - Painel operacional (SLA/Prod/Pend) e Admin (usuários/escopos).
  - Exports GeoJSON com RBAC/DLP.
  - Dash NOC: p95, error rate, filas (sync/ETL), alertas.
- Critérios de saída
  - Exports respeitam RBAC/DLP, com rate limiting.
  - Alertas acionáveis e runbooks básicos.

### M4 — Expansão + Homologação

- Entregáveis
  - Stubs 501 para `/analytics`, `/rotas`, `/voo` (contratos publicados).
  - Tiles/COG/WMTS operacional e configurado.
  - Webhooks e catálogo de eventos iniciais.
  - Caderno de testes concluído, dossiê final exportado.
- Critérios de saída
  - DoD completo por requisito do edital (vide `CADERNO_DE_TESTES.md`).

## 2. Governança de engenharia e arquitetura

### 2.1 Estrutura de repositório (monorepo)

```text
/techdengue
  /frontend            # Windsurf (web + PWA)
  /epi-api             # ETL EPI + indicadores + /relatorios/epi01
  /campo-api           # Atividades + evidências + /relatorios/evd01
  /relatorios-api      # Render PDF/A-1 + hash + catálogos
  /infra               # IaC (Terraform) + Helm/Compose + tileserver + s3 cfg
  /openapi             # openapi-v1.yaml + lint/SDK scripts
  /docs                # README, ROADMAP, Fundações, Caderno de Testes
  /db
    /flyway            # flyway.conf + sql/V1..Vn
```

- Pastas atuais em `docs/` permanecem como referência; `openapi-v1.yaml` é a fonte da verdade (duplicado `.txt` arquivado).

### 2.2 Branching, versionamento e commits

- Branching: trunk-based com PRs curtos; branches `release/x.y` quando necessário.
- Versionamento: SemVer por serviço; tag por pacote; changelog automatizado.
- Commits: Conventional Commits (feat/fix/docs/chore/refactor/test/build/ci).
- Proteções: PR com 2 reviews, checks verdes, code owners por módulo.

### 2.3 ADRs e decisões técnicas

- ADR-001 Backend stack: **FastAPI (Python)** escolhido como padrão.
  - Justificativa: OpenAPI nativo (Pydantic), PostGIS via GeoAlchemy2, menor curva de aprendizado, async nativo, comunidade ativa.
  - Alternativa: NestJS (TypeScript) para equipes com preferência TS; ambos são produção-ready.
- ADR-002 Storage S3 (minio/cloud), política de versionamento e encryption (SSE-KMS).
- ADR-003 PWA offline-first (Service Worker + IndexedDB + estratégia de sync/idempotência).
  - Resolução de conflitos: **Last-Write-Wins (LWW)** com base em `updated_at` do servidor.
  - Idempotência: cada evento tem `idempotency_key` (UUID); servidor ignora duplicatas.
  - Telemetria: logs de conflitos rejeitados (cliente desatualizado) para análise de padrões.
  - Retries: backoff exponencial (1s, 2s, 4s, 8s, max 64s) com DLQ após 10 tentativas.
- ADR-004 Observabilidade (OpenTelemetry + Prometheus + Loki/ELK) e correlação `X-Request-Id`.
- ADR-005 Gateway/API (rate limiting, DLP, CORS, headers de segurança).
- ADR-006 Frontend Stack: React 18 + Leaflet 1.9.4 (não Mapbox, baseado em SIVEPI Conta Ovos).
- ADR-007 Gerenciamento de Estado: Context API + hooks customizados (não Redux, padrão SIVEPI).
- ADR-008 Performance: Web Workers + virtualização + cache TTL 30s (validado SIVEPI).
- ADR-009 Offline-First: Service Worker + IndexedDB + fila sync (padrão SIVEPI campo).

### 2.4 Segurança e conformidade

- OIDC (authorization code + PKCE), JWKS cache, validação de escopos.
- RBAC por escopos: `epi.read/write`, `campo.read/write`, `admin`.
- Mapeamento papéis (DB `auth_usuario.papel`) → escopos OAuth:

| Papel (DB) | Escopos OAuth | Acesso |
|---|---|---|
| GESTOR | epi.read, campo.read | Consulta EPI e Campo (sem escrita) |
| VIGILANCIA | epi.read, epi.write | ETL, mapas, relatórios EPI |
| CAMPO | campo.read, campo.write | Atividades, evidências, relatórios EVD |
| ADMIN | epi.*, campo.*, admin | Acesso total + gestão de usuários |

- DLP em rotas de export/download (mascara/remoção de campos sensíveis).
- Gestão de segredos: injeção via vault/secret manager; sem segredos no repositório; rotação 90 dias.
- Logging seguro (sem PII sensível); retenção 90d quente, >90d S3, purge após 1 ano (LGPD).

### 2.5 Observabilidade e SRE

- Logs JSON estruturados (nível, serviço, rota, status, latency_ms, user_id, x_request_id).
- Métricas: requests_total, error_rate, latency_p95/p99, filas (sync/ETL), jobs em andamento.
- Tracing distribuído (propagação context/baggage, sample rate controlado).
- Dashboards por serviço e alertas (5xx > 2% por 5 min; p95 > 800 ms por 10 min).
- **SLOs por rota crítica**:

| Rota | SLO (p95) | SLO (error rate) | Alerta (threshold) |
|---|---|---|---|
| GET /indicadores | ≤ 500 ms | ≤ 0.5% | p95 > 800 ms por 5 min |
| GET /mapa (≤10k feições) | ≤ 4000 ms | ≤ 1% | p95 > 6000 ms por 5 min |
| POST /etl/epi/upload | ≤ 2000 ms | ≤ 1% | p95 > 3000 ms por 5 min |
| POST /atividades/{id}/evidencias | ≤ 1500 ms | ≤ 2% | p95 > 2500 ms por 5 min |
| GET /relatorios/epi01 | ≤ 8000 ms | ≤ 1% | p95 > 12000 ms por 5 min |
| GET /exports/atividades.geojson | ≤ 3000 ms | ≤ 1% | p95 > 5000 ms por 5 min |

- Runbooks e playbooks por tipo de incidente (5xx, latência, fila travada).

### 2.6 Qualidade e testes

- Pirâmide de testes: unit > integração (DB/ETL) > contrato (OpenAPI) > E2E (web/PWA) > não funcionais (carga/perf/segurança/a11y).
- Testes de contrato (Prism/Stoplight + schemathesis/contract tests) obrigatórios no CI.
- Caderno de testes em `docs/CADERNO_DE_TESTES.md` e evidências versionadas.
- Qualidade de código: lint/format (TS/ESLint/Prettier ou flake8/black), pre-commit.
- Scans: SAST e dependências, secret scan.

### 2.7 Dados e migrações

- Migrações Flyway versionadas (`V1..Vn`) e idempotentes quando possível.
- Mecanismo de rollback e scripts de verificação pós-migração.
- Papéis de banco por ambiente/serviço; backups automatizados; retenção.
- Views/materializações para mapas por período; índices monitorados.

### 2.8 Gestão de APIs (OpenAPI)

- Fonte: `docs/openapi/openapi-v1.yaml` com lint (Redocly/OpenAPI CLI) no CI.
- Mock: Prism para desenvolvimento; collection httpie/VS Code incluída.
- Versionamento: rotas sob `/v1`; breaking changes via `/v2` com deprecação controlada.
- SDKs: geração automatizada (TS/Python) e publicação interna por pacote.

### 2.9 CI/CD e Deploy (GitHub + Netlify)

- GitHub Actions (monorepo):
  - Triggers: `pull_request` e `push` em `main`.
  - Jobs: `openapi:lint` → `frontend:lint+test+build` → `backend:test`.
  - Node 20 com cache do npm; upload de artefatos (build, cobertura).
  - Checks obrigatórios para merge (testes, lint, contrato OK).
- Netlify (frontend):
  - Integração via GitHub para Deploy Previews por PR.
  - Build: `npm ci && npm run build` (Vite/React).
  - Publish: `dist/` (ou `build/` conforme scaffold escolhido).
  - Ambiente: mapear `REACT_APP_*` e chaves públicas (nunca segredos).
- Exemplo `netlify.toml` (ajustar após criar o frontend):

```toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "20"

[[plugins]]
  package = "@netlify/plugin-lighthouse"

[dev]
  command = "npm run dev"
  port = 5173
```

### 2.10 Configuração Frontend (env)

- `REACT_APP_API_URL` (ex.: `/api` em dev; URL do gateway em prod)
- `REACT_APP_WS_URL` (ex.: `wss://.../ws` para atualizações em tempo real)
- `MAP_TOKEN` (Mapbox/llaves quando aplicável)
- `TILES_BASE_URL` (tileserver/WMTS)
- `FEATURE_FLAGS` (toggles de UI, ex.: `temporal_week=true`)

### 2.11 Suporte, SLA e Garantia

- **Níveis de Serviço (SLA)**:

| Severidade | Descrição | Tempo de Resposta | Tempo de Solução | Canal |
|---|---|---|---|---|
| P1 - Crítico | Sistema indisponível ou perda de dados | ≤ 1 hora | Workaround ≤ 8h; Definitivo ≤ 24h | Telefone + e-mail |
| P2 - Alto | Funcionalidade crítica inoperante | ≤ 4 horas | ≤ 48 horas | E-mail + portal |
| P3 - Médio | Funcionalidade secundária com impacto moderado | ≤ 8 horas | ≤ 5 dias úteis | Portal |
| P4 - Baixo | Dúvidas, melhorias, documentação | ≤ 24 horas | ≤ 10 dias úteis | Portal |

- **Janelas de Atendimento**: 8x5 (segunda a sexta, 8h-17h, horário de Brasília); P1 com plantão 24x7 via telefone emergencial.
- **Garantia de Software**: Correção de defeitos (bugs) sem custo adicional durante vigência do contrato (12 meses + renovação).
- **Garantia de Equipamentos/Insumos**: Mínimo 3 meses (conforme TR), incluindo substituição e custos de transporte/mão de obra.
- **Canais de Suporte**:
  - Portal de atendimento (tickets rastreáveis).
  - E-mail: suporte@techdengue.com.
  - Telefone emergencial (P1): +55 65 XXXX-XXXX.
- **Métricas de Qualidade**:
  - Taxa de resolução no primeiro contato (FCR) ≥ 70%.
  - Satisfação do usuário (CSAT) ≥ 4.0/5.0.
  - Disponibilidade do sistema ≥ 99% (exceto janelas de manutenção programadas).

### 2.12 Aceite, Homologação e Laudo de Aceitabilidade

- **Entrega Técnica** (conforme TR):
  - Apresentação ao proprietário de recursos, funcionalidades, instruções fundamentais.
  - Manual de operação e manutenção em língua portuguesa.
  - Treinamento in loco para operação e manutenção preventiva (sem ônus adicional).
- **Homologação por Requisito**:
  - Cada requisito do edital/TR executado conforme casos de teste do `CADERNO_DE_TESTES.md`.
  - Evidências: prints, logs, vídeos, relatórios gerados.
  - Resultado esperado vs obtido documentado.
- **Laudo de Aceitabilidade**:
  - Emitido pela comissão técnica após validação da PoC e homologação.
  - Aprovação integral: aceite definitivo.
  - Aprovação condicional: reentrega com prazo de 5 dias úteis (corrigir não conformidades).
  - Rejeição: convocação do licitante subsequente ou anulação.
- **Rejeição**:
  - Objeto em desacordo com Edital, TR, contrato ou especificações técnicas.
  - Prazo: contratada notificada com 48h para manifestação; 5 dias úteis para correção ou substituição.
- **Aceite Definitivo**: Formalizado via termo de aceite assinado digitalmente; habilita pagamento e início de garantia/SLA.

## 3. Design por trilhas (implementação)

### 3.1 ETL EPI e Conectores Externos (PoC)

- Upload multipart para S3 (presigned) + enfileiramento de job.
- Validação (schema CSV-EPI01), qualidade (erros/avisos/linhas afetadas), relatório JSON.
- Carga na tabela `indicador_epi` (Timescale hypertable por `competencia`).
- **Conectores PoC SINAN/LIRAa** (demonstração com datasets de exemplo):
  - Endpoint `POST /etl/sinan/import` (CSV público SINAN Arboviroses).
  - Endpoint `POST /etl/liraa/import` (CSV LIRAa com IIP/IBR).
  - Normalização: campos `fonte` ('SINAN', 'LIRAa', 'Municipal') e `versao_indicador`.
  - Validação de municípios (cod_ibge) e competências.
- APIs: `POST /etl/epi/upload`, `GET /etl/epi/qualidade/{carga_id}`, `GET /indicadores`.
- Observabilidade: métricas de tempo de validação, taxa de erro, throughput.

### 3.2 Mapa Vivo

- **Clustering inteligente por criticidade** (padrão SIVEPI Conta Ovos):
  - Níveis: Sem Risco (verde) → Baixo (amarelo) → Médio (laranja) → Alto (vermelho) → Crítico (roxo)
  - Ícones dinâmicos baseados em SLA, evidências, status
  - Popups detalhados com dados da atividade
- Camadas choropleth (viridis) para indicadores (incidência/100k, IPO/IDO/IVO/IMO)
- **Virtualização de markers**: renderizar apenas viewport, limites por zoom
- **HeatMap configurável**: intensidade, raio, blur ajustáveis
- Materializações por período, cache TTL 30s
- Performance: p95 ≤ 4s (≤10k feições), debounce 150ms

### 3.3 Campo, Evidências, e-Denúncia + Chatbot (PoC)

- Modelo de eventos (append-only) para fila de sync com `idempotency_key`.
- **Web Worker para validação** de evidências (SHA-256, metadados, geotag)
- Captura com watermark e cálculo SHA-256 local; manifesto com Merkle root.
- **IndexedDB local**: stores `atividades`, `evidencias`, `insumos`, `fila_sync`, `denuncias`
- **Service Worker**: cache first (assets), network first (dados), queue (mutations)
- Upload direto para S3 via presigned; reconciliação servidor/cliente por `updated_at`.
- **Módulo e-Denúncia + Chatbot** (PoC edital):
  - Canal público de denúncias (formulário web + app móvel).
  - Chatbot reativo simples (FSM local, flows pré-definidos, sem APIs externas).
  - Fluxos: localização → tipo de foco → descrição → foto opcional → confirmação.
  - Handoff para formulário detalhado se chatbot não resolver.
  - Triagem automática: denúncia → `atividade` (origem='DENUNCIA', status='CRIADA').
  - API: `POST /denuncias`, `GET /denuncias/{id}`, integração com `campo-api`.
- APIs: `POST/GET /atividades`, `PATCH /atividades/{id}`, `POST/GET /atividades/{id}/evidencias`.
- **Hook `useWebWorker`** para processamento paralelo

### 3.4 Relatórios (EPI01/EVD01)

- **Ferramenta PDF/A-1**: WeasyPrint (Python) ou LibreOffice headless (fallback).
  - Validação: veraPDF no CI para garantir conformidade PDF/A-1b.
  - Template: HTML + CSS → WeasyPrint → PDF/A-1.
- Pipeline de composição: dados + imagens (gráficos/mapa) + template → PDF/A-1.
- Hash SHA-256 no rodapé, armazenamento em `relatorios/` com versionamento.
- Linkagem e verificação de integridade (`hash_sha256` retornado na API).
- Metadados PDF: título, autor, data de geração, versão do sistema.

### 3.5 Exports Geo + DLP

- `GET /exports/atividades.geojson` com filtragem por escopo e mascaramento.
- Rate limiting e auditoria por `audit_log`.

### 3.6 Social Listening (PoC – IA Redes Sociais)

- **Objetivo PoC**: Demonstrar capacidade de "robôs virtuais" (IA) operando em redes sociais para detecção de surtos/reclamações.
- **Implementação PoC**:
  - Pipeline simulado com dataset offline (tweets/posts sintéticos sobre dengue/Aedes).
  - Conectores mock (sem uso de APIs Twitter/Facebook/Instagram).
  - NLP básico: detecção de palavras-chave ("dengue", "picada", "mosquito", "foco", "água parada").
  - Classificação de sentimento (negativo/neutro/positivo) e localização (se mencionada).
  - Geração de alertas: posts com sentimento negativo + localização → criar `atividade` (origem='ALERTA').
- **Dashboard**: Mapa de calor de menções, linha do tempo, top hashtags, alertas gerados.
- **API PoC**: `GET /social-listening/alerts`, `GET /social-listening/dashboard`.
- **Nota**: Em produção, substituir por conectores reais (autorizados) ou desabilitar se não contratado.

### 3.7 Drone Mission Simulator (PoC – VANTs)

- **Objetivo PoC**: Demonstrar planejamento de voo e operação VANTs com dispersão de larvicidas.
- **Implementação PoC**:
  - UI de planejamento: selecionar área no mapa (polígono), altitude, padrão de voo (grid/serpentina).
  - Cálculo de cobertura: área (ha), autonomia drone (bateria), taxa de dispersão larvicida.
  - Geração de waypoints (rota KML/GeoJSON exportável).
  - Simulação de missão: animação 3D da rota, status (em voo/dispersão/retorno), logs em tempo real.
  - Dados sintéticos: sem drone real, mas com validação de regras (ANAC, zonas proibidas).
- **API PoC**: `POST /voo/missoes`, `GET /voo/missoes/{id}`, `GET /voo/missoes/{id}/rota.kml`.
- **Dashboard**: Histórico de missões, cobertura acumulada (ha), insumos consumidos.
- **Nota**: Em produção, integrar com sistema de telemetria drone real ou manter como planejador.

### 3.8 Treinamento e Manuais

- **Treinamento In Loco** (exigido TR):
  - Turmas: até 20 participantes por turma.
  - Carga horária mínima: 8 horas (operação) + 4 horas (manutenção preventiva).
  - Material didático: slides, guias rápidos, vídeos tutoriais.
  - Certificado de participação.
- **Manuais em Português** (entregues na entrega técnica):
  - Manual do Usuário (operação do sistema, fluxos principais).
  - Manual do Administrador (gestão de usuários, configurações, backups).
  - Manual de Manutenção Preventiva (equipamentos/insumos, quando aplicável).
  - Guia de Troubleshooting (problemas comuns e soluções).
- **Documentação Online**: Wiki com tutoriais, FAQ, changelogs, release notes.

## 4. Ambientes, Deploy, Backups e DR

### 4.1 Ambientes

- **Local**: docker-compose para DB/serviços; Prism para mock; seeds mínimos.
- **Homolog**: CI/CD com deploy automático em merge para `main`, canário habilitado.
- **Produção**: janelas controladas (terças/quintas 10h-16h), blue/green/canary; feature flags para toggles.
- **Infra como código**: Terraform (S3, DB, rede) + Helm/K8s (serviços e ingress).

### 4.2 Backups e Disaster Recovery (DR)

- **Política de Backups**:
  - **Banco de Dados**: Backup completo diário (2h UTC-3), incremental a cada 6h; retenção 30 dias local + 90 dias S3 Glacier.
  - **Buckets S3**: Versionamento habilitado; replicação cross-region (opcional em produção); lifecycle para Glacier após 90 dias.
  - **Configurações e Secrets**: Backup semanal de configs (Terraform state, Helm values, secrets vault); versionamento Git.
- **Testes de Restauração**: Trimestral (validar RTO/RPO); simulação de falha com restore completo em ambiente de testes.
- **RTO/RPO Objetivos**:
  - **Homolog**: RTO 8h, RPO 6h.
  - **Produção**: RTO 4h, RPO 1h (dados críticos), 6h (dados operacionais).
- **Plano de Contingência**:
  - Runbook de restauração por tipo de falha (corrupção DB, perda S3, falha região).
  - Equipe de plantão 24x7 para P1 (incidentes críticos).
  - Comunicação: alerta automático via Slack/e-mail para stakeholders em caso de acionamento DR.

## 5. Cronograma sugerido (sprints de 2 semanas)

- Sprint 1–2 (M0): monorepo, CI/CD mínimos, DB+S3, OpenAPI v1, OIDC homolog, observabilidade básica.
- Sprint 3–4 (M1): ETL EPI completo + mapa vivo + EPI01.
- Sprint 5–6 (M2): PWA offline + evidências + EVD01.
- Sprint 7 (M3): Operacional/Admin + Exports/DLP + NOC.
- Sprint 8 (M4): Stubs/tiles/webhooks + caderno de testes + dossiê.

## 6. Critérios de aceite por fase

- Alinhados ao `ROADMAP.md` e `1_Fundacoes.md` (checklists M0–M4).
- Caderno de testes atualizado com evidências por requisito.
- Alertas e dashboards publicados; logs e métricas auditáveis.

## 7. Riscos e mitigação

- Atraso em integrações OIDC/S3 → ambientes de mock e chaves provisórias.
- Performance de mapas/dados → materializações, índices, limites de feições e caching.
- Sincronização offline conflituosa → idempotência, LWW e telemetria de falhas.
- PDFs/A-1 e hash → padronização de ferramenta e teste de conformidade contínuo.

## 8. Conhecimentos SIVEPI Conta Ovos Integrados

### Padrões Validados Incorporados
- ✅ **Arquitetura modular** com hooks customizados (`useDataProcessor`, `useMetrics`, `useWebWorker`)
- ✅ **Clustering inteligente** baseado em risco epidemiológico (adaptado para criticidade de atividades)
- ✅ **Performance otimizada**: cache TTL 30s, debounce 150ms, virtualização de markers
- ✅ **PWA offline-first**: Service Worker + IndexedDB + fila de sincronização (padrão SIVEPI)
- ✅ **Web Workers**: processamento paralelo de validações, estatísticas e exports
- ✅ **Design System epidemiológico**: paleta de cores por níveis de risco, componentes reutilizáveis
- ✅ **Timeline temporal**: filtros por competência (último dia do mês), semanas epidemiológicas
- ✅ **Insights acionáveis**: dashboard com KPIs, alertas automáticos, recomendações contextuais
- ✅ **Testes abrangentes**: Jest + RTL (>95% cobertura), Cypress E2E

### Referências Técnicas
- `docs/CONHECIMENTOS_CONTA_OVOS.md`: padrões detalhados
- ADRs 006-009: decisões baseadas em SIVEPI
- Stack validada: React 18 + Leaflet 1.9.4 + PWA

---

## 9. Próximos passos imediatos (M0)

- Consolidar OpenAPI (feito) e ativar lint/CI.
- Subir DB local e aplicar Flyway `V1..V4`.
- Provisionar buckets S3 com versionamento e SSE.
- Configurar OIDC (homolog) e RBAC básico.
- Habilitar logs estruturados e métricas p95 por rota.

---

Referências: `docs/1_Fundacoes.md`, `docs/ROADMAP.md`, `docs/openapi/openapi-v1.yaml`, `docs/CADERNO_DE_TESTES.md`.
