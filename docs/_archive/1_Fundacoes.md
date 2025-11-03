# M0 — Fundações (pré-dev) • Passo a passo completo

## 0.1 Repositório & pastas

```
/techdengue
  /frontend           # Windsurf (web + PWA campo)
  /epi-api            # ETL EPI + indicadores + EPI01
  /campo-api          # Atividades + evidências + EVD01
  /relatorios-api     # Render PDF/A-1 + hash + catálogos
  /infra              # k8s/helm/compose, tileserver, s3 cfg
  /openapi            # openapi-v1.yaml (já criado)
  /docs               # ROADMAP.md, guias, caderno de testes
  /db
    /migrations       # Liquibase/Flyway
    /seeds
```

## 0.2 Variáveis de ambiente (baseline)

```
OIDC_ISSUER, OIDC_CLIENT_ID, OIDC_CLIENT_SECRET
DB_URL, DB_USER, DB_PASS
S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_ETL, S3_BUCKET_EVID, S3_BUCKET_REL
MAP_TOKEN (Mapbox/llaves), TILES_BASE_URL
JWT_AUDIENCE, JWT_JWKS_URI
```

## 0.3 Banco de dados (PostgreSQL + PostGIS + Timescale)

### 0.3.1 Extensões

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS timescaledb;
```

### 0.3.2 Esquema mínimo (DDL inicial)

```sql
-- Tabela usuários (RBAC simples)
CREATE TABLE auth_usuario (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  nome TEXT NOT NULL,
  papel TEXT NOT NULL CHECK (papel IN ('GESTOR','VIGILANCIA','CAMPO','ADMIN')),
  territorio_scope TEXT,     -- ex: '3106200,*' ou 'URS:XX'
  ativo BOOLEAN DEFAULT TRUE,
  criado_em TIMESTAMPTZ DEFAULT now()
);

-- Log de auditoria
CREATE TABLE audit_log (
  id BIGSERIAL PRIMARY KEY,
  actor_id UUID REFERENCES auth_usuario(id),
  recurso TEXT NOT NULL,     -- 'atividade','indicador_epi', etc.
  acao TEXT NOT NULL,        -- 'CREATE','UPDATE','EXPORT','LOGIN'
  payload_resumido JSONB,
  criado_em TIMESTAMPTZ DEFAULT now()
);

-- Indicadores epidemiológicos (Timescale)
CREATE TABLE indicador_epi (
  municipio_cod_ibge TEXT NOT NULL,
  municipio_nome TEXT,
  competencia DATE NOT NULL,
  populacao INT,
  casos INT,
  incidencia_100k NUMERIC,
  ipo NUMERIC, ido NUMERIC, ivo NUMERIC, imo NUMERIC,
  fonte TEXT,
  versao_indicador TEXT DEFAULT '1.0.0',
  calc_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (municipio_cod_ibge, competencia)
);
SELECT create_hypertable('indicador_epi','competencia', if_not_exists=>TRUE);

-- Atividades de campo
CREATE TABLE atividade (
  id UUID PRIMARY KEY,
  origem TEXT CHECK (origem IN ('DENUNCIA','PLANO','ALERTA')),
  municipio_cod_ibge TEXT NOT NULL,
  bairro TEXT,
  equipe TEXT,
  sla_deadline TIMESTAMPTZ,
  status TEXT NOT NULL CHECK (status IN ('CRIADA','EM_ANDAMENTO','ENCERRADA')),
  criado_em TIMESTAMPTZ DEFAULT now(),
  atualizado_em TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_atividade_status ON atividade(status);
CREATE INDEX idx_atividade_mun ON atividade(municipio_cod_ibge);

-- Evidências
CREATE TABLE evidencia (
  id UUID PRIMARY KEY,
  atividade_id UUID REFERENCES atividade(id) ON DELETE CASCADE,
  uri TEXT NOT NULL,
  hash_sha256 TEXT NOT NULL,
  lat NUMERIC, lon NUMERIC,
  tipo TEXT CHECK (tipo IN ('FOTO','VIDEO')) NOT NULL,
  capturado_em TIMESTAMPTZ NOT NULL,
  criado_em TIMESTAMPTZ DEFAULT now()
);

-- Insumos
CREATE TABLE insumo_mov (
  id UUID PRIMARY KEY,
  atividade_id UUID REFERENCES atividade(id) ON DELETE CASCADE,
  nome TEXT NOT NULL,
  lote TEXT,
  qtd NUMERIC NOT NULL,
  unidade TEXT NOT NULL,
  validade DATE,
  criado_em TIMESTAMPTZ DEFAULT now()
);
```

### 0.3.3 Seeds mínimos

```sql
INSERT INTO auth_usuario (id,email,nome,papel,territorio_scope)
VALUES (gen_random_uuid(),'admin@aero.com','Admin','ADMIN','*');
```

## 0.4 Buckets S3 (estratégia e política)

* Buckets separados:
  `etl/` (planilhas e relatórios de qualidade),
  `evidencias/` (mídias + manifests),
  `relatorios/` (PDF/CSV assinados).
* **Versionamento ligado**, **server-side encryption (KMS)**.
* **Presigned URLs** para upload/download.
* Pastas:

```
evidencias/{municipio}/{atividade_id}/{arquivo}
relatorios/{tipo}/{YYYY}/{MM}/{arquivo}
etl/{competencia}/{upload_id}/{arquivo}
```

## 0.5 Observabilidade mínima

* **Logs JSON** com `x_request_id`, `user_id`, `rota`, `latency_ms`, `status`.
* Métricas por rota: `requests_total`, `errors_total`, `latency_p95`.
* Alertas iniciais: erro 5xx > 2% (5 min), p95 > 800 ms (10 min).

## 0.6 OpenAPI v1 + Mock

* Arquivo `openapi/openapi-v1.yaml` (já enviado).
* Subir **mock server** (ex.: prism ou stoplight) apontando para esse YAML.

**Checklist M0 (Done)**

* [ ] DB + extensões ativas
* [ ] Buckets S3 com versionamento
* [ ] OIDC configurado (homolog)
* [ ] OpenAPI v1 publicado + mock
* [ ] Logs/metrics básicos ativos

---

# M1 — Mapa Vivo, ETL EPI, Relatório EPI01 • Passo a passo

## 1.1 ETL EPI (upload, validação, qualidade)

### 1.1.1 Esquema CSV aceito (CSV-EPI01)

```
municipio_cod_ibge,municipio_nome,competencia,populacao,casos,incidencia_100k,ipo,ido,ivo,imo,fonte,versao_indicador
3106200,Belo Horizonte,2025-09-30,2500000,345,13.8,1.2,0.8,0.5,0.3,SIVEP-ARBOVIROSES,1.0.0
```

### 1.1.2 Regras de qualidade

* `municipio_cod_ibge` (7 dígitos) existente na tabela de municípios.
* `competencia` = último dia do mês (ou converter para esse padrão).
* `populacao > 0`, `casos >= 0`, `incidencia_100k = casos/pop * 100000` (tolerância ±0,1).
* Sem datas futuras.
* **Relatório de qualidade** (JSON) com: `erros[]`, `avisos[]`, `linhas_afetadas`, `percentual_cobertura`.

### 1.1.3 Fluxo API (resumo)

* `POST /etl/epi/upload` → armazena arquivo em `etl/` e enfileira job de validação/carga.
* `GET /etl/epi/qualidade/{carga_id}` → retorna JSON e link para relatório detalhado.

## 1.2 Mapa & Camadas

* Biblioteca: **Leaflet** ou **MapLibre** (livre), com **clusterização** para pontos.
* Camadas:

  * **Choropleth**: incidência/100k, IPO/IDO/IVO/IMO (por bairro/município).
  * Paletas **daltônicas** (viridis).
* Performance: materializar `view` por período; limitar 10k features na tela; **tile cache** para base.

## 1.3 Relatório EPI01 (PDF/CSV)

* PDF/A-1, capa com município/competência & **hash** no rodapé.
* Gráficos: tendência (linhas), comparação (barras), mapa temático estático (rasterizado).
* CSV igual ao **CSV-EPI01** (acima) para a competência filtrada.

**Checklist M1**

* [ ] ETL valida e gera relatório de qualidade
* [ ] Mapas p95 ≤ 4s (10k features)
* [ ] EPI01 disponível (PDF/CSV) com hash

---

# M2 — Campo (MVP robusto) + EVD01 • Passo a passo

## 2.1 PWA (offline-first básico)

* **IndexedDB**: stores `atividades`, `evidencias`, `insumos`, `fila_sync`.
* **Estratégia de sync**:

  * Cada ação gera um **evento** (append-only) com `idempotency_key`.
  * Reenvio com **backoff exponencial**.
  * Conflito: regra *last-write-wins* com carimbo de `updated_at` do servidor.

## 2.2 Captura de mídia (geotag + watermark + hash)

* Ao capturar:

  * Inserir **watermark** “município | atividade_id | lat/lon | data/hora (UTC-3)”.
  * Calcular **SHA-256** do arquivo (`hash_sha256`).
  * Gerar **Merkle root** do pacote quando encerrar a atividade (manifests).
* Upload:

  * Se online: **presigned URL** direto para S3 `evidencias/{mun}/{atividade_id}/...`.
  * Se offline: enfileirar em `fila_sync`.

### Manifest (JSN-EVD01) exemplo mínimo

```json
{
  "atividade_id": "uuid-...",
  "midias": [
    {"uri":"s3://.../p1.jpg","hash":"sha256:...","ts":"2025-10-31T10:42:00-03:00","lat":-19.9,"lon":-43.9}
  ],
  "assinaturas": {"root_hash":"sha256:..."}
}
```

## 2.3 Checklists e Insumos

* Checklists com **itens obrigatórios** condicionais (ex.: foco = piscina exige foto).
* Insumos: bloquear baixa de **lote vencido**; registrar quantidade/unidade.

## 2.4 Relatório EVD01 (PDF/A-1)

* Capa: id atividade, município, data.
* Corpo: mapa do ponto/polígono, fotos (miniaturas) com metadados, **root hash**.
* Rodapé: `sha256:...` e `build_id`.

**Checklist M2**

* [ ] Agenda e execução de atividade completas
* [ ] Evidências com hash e geotag; sync resiliente
* [ ] EVD01 emitido e verificável

---

# M3 — Operação & Admin; Exports; Observabilidade/DLP • Passo a passo

## 3.1 Painel Operacional

* KPIs: `%SLA`, `atividades/dia`, `%evidências válidas`, `pendências`.
* Filtros por município/equipe/período; **drill-down** para a lista de atividades.

## 3.2 Export GeoJSON (RBAC/DLP)

* `GET /exports/atividades.geojson`
* SQL (exemplo) para gerar features:

```sql
SELECT jsonb_build_object(
  'type','Feature',
  'geometry', ST_AsGeoJSON(geom)::jsonb,
  'properties', to_jsonb(a) - 'geom'
)
FROM atividades_view a;
```

* **DLP**: se papel ≠ ADMIN, remover campos sensíveis (`- 'comentarios_privados'`), aplicar **rate-limit**.

## 3.3 Admin

* CRUD usuários, reset 2FA, escopos territoriais (`territorio_scope`).
* Parâmetros (ex.: tolerância de cálculo, janelas de SLA).

## 3.4 Observabilidade (NOC) + DLP

* Dashboard NOC: `error_rate`, `latency_p95`, fila de sync, ETL status.
* Alertas: já configurados em M0; agora com **rota de plantão**.
* DLP: regras aplicadas em rotas de export e download de relatórios.

**Checklist M3**

* [ ] Painel operacional fechado
* [ ] Export Geo respeita RBAC/DLP
* [ ] Admin funcionando
* [ ] NOC com alertas básicos

---

# M4 — Preparação para expansão + Homologação • Passo a passo

## 4.1 Stubs (Analytics/Rotas/Drone)

* Endpoints já no **OpenAPI** retornando **501** com payload:

```json
{"status":"NOT_IMPLEMENTED","message":"Endpoint planejado para Fase 2"}
```

* Motivo: manter **contrato estável** para futura ativação sem quebrar clientes.

## 4.2 Tiles/COG/WMTS

* Publicar **tileserver** (ex.: `tileserver-gl` ou `titiler` para COG).
* Testar uma camada simples (base municipal) e configurar `TILES_BASE_URL`.

## 4.3 Webhooks & Catálogo de Eventos

* Eventos iniciais:

  * `atividade.created`
  * `atividade.closed`
  * `etl.ok`
* Tabela `webhook_subscriber(id,url,escopo,ativo)` + retentativas (DLQ).

## 4.4 Homologação (Caderno de Testes)

* Para cada requisito do edital:

  * **Caso de teste** → **Passos** → **Dados usados** → **Evidências (print/log)** → **Resultado esperado/obtido**.
* Exportar em **PDF** e anexar ao dossiê.

## 4.5 Anexos do dossiê (curtos e diretos)

* Plano de Implantação (Gantt 4 sprints)
* Cronograma Físico-Financeiro
* ROPA/DPIA (resumo 2 págs)
* Plano de Treinamento (turmas/carga horária)
* Equipe do Projeto (papéis/senioridade/% alocação)
* Requisitos Técnicos (navegador/rede/mobile)
* Termos de Dados & IP

**Checklist M4**

* [ ] Stubs publicados
* [ ] Tiles/COG prontos
* [ ] Webhooks mínimos ativos
* [ ] Caderno de testes fechado
* [ ] Dossiê final exportado

---

## Windsurf (frente de desenvolvimento) — primeiras rotas/componentes

### Rotas Web

* `/login` (SSO)
* `/mapa` (camadas EPI)
* `/etl` (upload + qualidade)
* `/painel-epi`
* `/operacional`
* `/relatorios`
* `/admin`

### PWA Campo

* `/agenda`
* `/atividade/:id` (abas: checklist | evidências | insumos | encerrar)
* `/fila-envio`
* `/config` (export logs, permissões)

### Estado & dados

* **Web**: Query lib + cache por chave de filtro; invalidação após ETL.
* **PWA**: IndexedDB mapeada 1:1 com modelos; fila de eventos idempotentes.

---

## Testes essenciais (aceitação)

* **ETL**: arquivo válido → carga OK; inválido → relatório de erro.
* **Mapa**: troca de camadas/legendas sem travar; até 10k feições p95 ≤ 4s.
* **Campo**: criar/atribuir/encerrar com mídia → gera EVD01 com hash.
* **Offline**: registrar evidência sem rede → sincroniza automática ao voltar.
* **Relatórios**: EPI01/EVD01 baixáveis; CSV bate com dicionário.
* **RBAC/DLP**: usuário “VIGILÂNCIA” não consegue exportar campos restritos.
* **Observabilidade**: logs com `x_request_id`, métricas visíveis, alerta dispara.

