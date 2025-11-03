# Caderno de Testes — TechDengue (Template)


## 1. Introdução

 
- **Objetivo:** comprovar atendimento item a item do edital.
- **Versão do sistema:** [preencher]
- **OpenAPI ref:** docs/openapi/openapi-v1.yaml (fonte da verdade)


## 2. Escopo e critérios

 
- **Abrangência:** módulos EPI (ETL/Mapa/Relatórios), Campo (PWA/evidências/insumos), Operacional/Admin, Exports/DLP.
- **Critérios de aprovação:** 100% casos críticos OK; sem severidade Alta aberta.


## 3. Ambiente de testes

 
- **Backend:** [preencher] | DB: PostgreSQL+PostGIS+Timescale | Buckets S3 com versionamento.
- **Frontend:** Windsurf skeleton + PWA offline.
- **Credenciais:** perfis ADMIN, VIGILANCIA, CAMPO.


## 4. Matriz de rastreabilidade

 
| Requisito (edital) | Caso(s) | Evidência(s) | Status |
|---|---|---|---|
| EPI-ETL-01 | TC-EPI-001 | print+log | Pendente |
| CAMPO-MIDIA-01 | TC-CAM-010 | PDF EVD01 | Pendente |


## 5. Casos de Teste


### 5.1 ETL EPI

 
- **TC-EPI-001 — Upload válido gera qualidade OK**
  - Pré-condições: usuário com escopo epi.write; CSV conforme `CSV-EPI01`.
  - Passos:
    1. POST `/etl/epi/upload` com arquivo válido.
    2. GET `/etl/epi/qualidade/{carga_id}` até status OK.
  - Dados: `docs/1_Fundacoes.md` CSV-EPI01 exemplo.
  - Resultado esperado: `erros=0`, `avisos<=N`, indicadores carregados.
  - Evidências: request/response JSON, captura da planilha, logs.

- **TC-EPI-002 — Upload inválido gera relatório de erro**
  - Passos: enviar CSV com `competencia` inválida.
  - Esperado: `erros>0` e lista de linhas afetadas.


### 5.2 Mapas EPI

 
- **TC-MAP-001 — Choropleth e troca de camadas p95 ≤ 4s**
  - Passos: carregar `/mapa`, alternar camadas IPO/IDO/IVO/IMO, medir p95.
  - Esperado: p95 ≤ 4s com ≤10k feições; legendas corretas.


### 5.3 Relatório EPI01

 
- **TC-RPT-001 — Geração PDF/A-1 com hash no rodapé**
  - Passos: GET `/relatorios/epi01` (municipio/competencia).
  - Esperado: retorno de `pdf_url`, `hash_sha256`; hash confere com arquivo baixado.


### 5.4 Campo (PWA)

 
- **TC-CAM-010 — Captura mídia com geotag, watermark e hash**
  - Passos: registrar evidência offline; reconectar; sincronizar fila.
  - Esperado: `hash_sha256` persistido; `lat/lon` salvos; upload via presigned URL.

- **TC-CAM-011 — Encerrar atividade gera EVD01**
  - Passos: anexar mídias; encerrar; GET `/relatorios/evd01`.
  - Esperado: PDF/A-1 com miniaturas e root hash.


### 5.5 Exports & DLP

 
- **TC-EXP-001 — GeoJSON respeita RBAC/DLP**
  - Passos: GET `/exports/atividades.geojson` com perfis diferentes.
  - Esperado: campos sensíveis mascarados fora de ADMIN; rate-limit aplicado.


### 5.6 Operacional & Admin

 
- **TC-OP-001 — KPIs e filtros**
  - Esperado: KPIs `%SLA`, `atividades/dia`, `%evidências válidas` corretos.
- **TC-ADM-001 — CRUD usuários e escopos**
  - Esperado: criação, alteração papel e `territorio_scope` efetivos.


## 6. Dados de teste

 
- Usuários: ADMIN, VIGILANCIA, CAMPO.
- Amostras: `indicador_epi` (BH), 1 atividade semente, 1 denúncia (ver V4__seed_minimo.sql).


## 7. Evidências

 
- Repositório de evidências: `docs/evidencias/<id-caso>/` com prints, logs, PDFs.


## 8. Resultados e não conformidades

 
| Caso | Resultado | Severidade | Ação corretiva | Responsável | Prazo |
|---|---|---|---|---|---|
| TC-EPI-001 | Aprovado | - | - | - | - |


## 9. Assinaturas

 
- Testador: __________________ Data: ____/____/____
- PO/Cliente: ________________ Data: ____/____/____
