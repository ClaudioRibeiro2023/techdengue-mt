# M2 - Campo MVP + EVD01 | Plano de Implementação Faseado

**Versão**: 1.0.0  
**Data Início**: 02/11/2025  
**Previsão Conclusão**: 4-6 semanas  
**Status**: 🟡 **PLANEJAMENTO**

---

## 📋 Visão Geral M2

### Objetivo

Implementar sistema de gestão de atividades de campo com captura de evidências (foto/vídeo), sincronização offline-first resiliente e geração de relatórios EVD01 em PDF/A-1.

### Escopo

**Componentes:**
- 🏗️ **Campo API** - Backend para atividades e evidências
- 📱 **PWA Offline-First** - Frontend web com suporte offline
- 📄 **Relatório EVD01** - PDF/A-1 com miniaturas e hash Merkle
- ☁️ **Sincronização** - Fila idempotente com resolução de conflitos

**Fora do Escopo M2:**
- Analytics/rotas/voo (M4)
- Painéis Admin completos (M3)
- Webhooks/eventos (M4)

---

## 🎯 Entregáveis M2

### M2.1 - Campo API: Modelo de Dados e Schemas

**Duração**: 3 dias

- [ ] Schema Pydantic para `Atividade`
  - id, status (CRIADA/EM_ANDAMENTO/CONCLUIDA/CANCELADA)
  - origem (MANUAL/IMPORTACAO/ALERTA)
  - tipo (VISTORIA/LIRAa/NEBULIZACAO/etc)
  - municipio_cod_ibge, localizacao (Point)
  - timestamps (criado_em, iniciado_em, encerrado_em)
  - metadata JSONB (customizável)
  
- [ ] Schema Pydantic para `Evidencia`
  - id, atividade_id (FK)
  - tipo (FOTO/VIDEO/DOCUMENTO)
  - hash_sha256, tamanho_bytes
  - url_s3 (storage)
  - metadata (geotag, watermark_info, camera_info)
  - timestamps

- [ ] Enums para estados e tipos
- [ ] Validações customizadas (geotag MT, tamanho max 50MB)

**Critérios de Aprovação:**
- ✅ Schemas passam validação Pydantic
- ✅ Docs inline completos
- ✅ Type hints 100%

### M2.2 - Campo API: CRUD de Atividades

**Duração**: 5 dias

- [ ] POST `/api/atividades` - Criar atividade
- [ ] GET `/api/atividades` - Listar com filtros (status, municipio, data)
- [ ] GET `/api/atividades/{id}` - Detalhes
- [ ] PATCH `/api/atividades/{id}` - Atualizar status/metadata
- [ ] DELETE `/api/atividades/{id}` - Cancelar (soft delete)

**Validações:**
- Transições de estado válidas (CRIADA → EM_ANDAMENTO → CONCLUIDA)
- RBAC: CAMPO pode criar, GESTOR pode cancelar
- Município deve existir no sistema

**Critérios de Aprovação:**
- ✅ 5 endpoints implementados e testados
- ✅ Transições de estado validadas
- ✅ Testes de integração (10+)

### M2.3 - Campo API: Upload de Evidências (S3)

**Duração**: 7 dias

- [ ] POST `/api/atividades/{id}/evidencias/presigned-url`
  - Gera presigned URL para upload direto ao S3
  - Valida tipo de arquivo (jpeg, png, mp4)
  - Retorna URL temporária (5min) + campos obrigatórios
  
- [ ] POST `/api/atividades/{id}/evidencias`
  - Registra evidência após upload bem-sucedido
  - Calcula/valida hash SHA-256
  - Extrai metadata (EXIF, geotag, dimensões)
  - Aplica watermark (timestamp + usuário)
  
- [ ] GET `/api/atividades/{id}/evidencias` - Listar evidências
- [ ] DELETE `/api/evidencias/{id}` - Remover (marca como deletada)

**Infraestrutura:**
- Bucket S3 `evidencias/` com versionamento
- Lifecycle: mover para Glacier após 90 dias
- Presigned URLs com 5min de validade

**Critérios de Aprovação:**
- ✅ Upload funcional via presigned URL
- ✅ Hash SHA-256 validado
- ✅ Metadata EXIF extraída corretamente
- ✅ Watermark aplicado (data/hora/usuário)

### M2.4 - PWA: IndexedDB e Sync Offline

**Duração**: 10 dias

**Service Worker:**
- [ ] Estratégia Network-First com fallback
- [ ] Cache de assets estáticos (HTML/JS/CSS)
- [ ] Cache de tiles de mapa (OpenStreetMap)

**IndexedDB:**
- [ ] Store `atividades` (sincronizadas do servidor)
- [ ] Store `atividades_pendentes` (fila de criação offline)
- [ ] Store `evidencias_pendentes` (fila de upload)
- [ ] Store `sync_log` (histórico de sincronizações)

**Sync Engine:**
- [ ] Background sync ao retornar online
- [ ] Retry com backoff exponencial (1s, 2s, 4s, 8s, max 64s)
- [ ] Idempotency key (UUID) por operação
- [ ] Resolução de conflitos LWW (Last-Write-Wins)
- [ ] DLQ (Dead Letter Queue) após 10 tentativas

**Critérios de Aprovação:**
- ✅ Funciona 100% offline (criar atividade, anexar foto)
- ✅ Sincroniza ao retornar online
- ✅ Conflitos resolvidos corretamente
- ✅ UI indica status de sync (pendente/sincronizando/erro)

### M2.5 - PWA: Captura de Mídia com Geotag

**Duração**: 5 dias

- [ ] Componente React `CameraCapture`
  - Acesso à câmera (navigator.mediaDevices)
  - Preview em tempo real
  - Botão captura com feedback visual
  
- [ ] Geolocalização automática
  - navigator.geolocation.getCurrentPosition
  - Precisão mínima 50m
  - Timeout 10s com fallback manual
  
- [ ] Watermark Client-Side
  - Canvas API para overlay
  - Informações: data/hora, usuário, coordenadas
  - Formato: [DD/MM/YYYY HH:MM] [@usuario] [-15.6014, -56.0967]

- [ ] Compressão antes do upload
  - JPEG quality 85%
  - Max width/height 1920px
  - Redução ~70% do tamanho

**Critérios de Aprovação:**
- ✅ Câmera abre em dispositivos móveis
- ✅ Geotag capturado automaticamente
- ✅ Watermark visível e legível
- ✅ Upload < 2MB por foto (compressão)

### M2.6 - Relatório EVD01: Geração PDF/A-1

**Duração**: 7 dias

- [ ] Schema `RelatorioEVD01Request`
  - atividade_id
  - incluir_miniaturas (bool)
  - formato (pdf/json)
  - tamanho_pagina (A1/A4) - padrão A4
  
- [ ] Serviço `EVD01PDFGenerator`
  - Suporte a múltiplos tamanhos: A1 (594x841mm) e A4 (210x297mm)
  - Layout A4: cabeçalho + dados da atividade + grid 4x4 miniaturas (max 16/página)
  - Layout A1: cabeçalho + dados da atividade + grid 8x8 miniaturas (max 64/página)
  - Hash individual de cada evidência
  - Root hash Merkle de todas as evidências
  - Footer com QR code (link de verificação)
  
- [ ] Endpoint GET `/api/relatorios/evd01`
- [ ] Cálculo Merkle Tree
  - Árvore binária de hashes SHA-256
  - Root hash no cabeçalho do PDF

**Critérios de Aprovação:**
- ✅ PDF/A-1 válido
- ✅ Miniaturas legíveis (max 16 por página)
- ✅ Root hash Merkle calculado corretamente
- ✅ QR code funcional

### M2.7 - Testes End-to-End

**Duração**: 5 dias

- [ ] Cenário 1: Criar atividade online → anexar foto → encerrar
- [ ] Cenário 2: Criar atividade offline → anexar foto offline → sync online
- [ ] Cenário 3: Conflito de atualização simultânea (LWW)
- [ ] Cenário 4: Retry após falha de rede (backoff exponencial)
- [ ] Cenário 5: Gerar relatório EVD01 com 10 fotos

**Ferramentas:**
- Playwright para E2E web
- Offline simulation (Service Worker)
- Network throttling (3G/offline)

**Critérios de Aprovação:**
- ✅ 5 cenários E2E passando
- ✅ Cobertura > 80%
- ✅ Performance dentro dos SLAs

### M2.8 - Documentação e OpenAPI

**Duração**: 3 dias

- [ ] Atualizar `docs/openapi_m2.yaml`
  - Schemas: Atividade, Evidencia, EVD01
  - Endpoints: CRUD atividades, upload evidências, relatórios
  
- [ ] Guia de uso PWA offline
  - Como funciona IndexedDB
  - Estratégias de sync
  - Troubleshooting comum
  
- [ ] README do Campo API
- [ ] Exemplos práticos (curl, Postman)

**Critérios de Aprovação:**
- ✅ OpenAPI validado (lint)
- ✅ Guias completos e testados
- ✅ Exemplos executáveis

---

## 📅 Cronograma Detalhado

| Semana | Fase | Duração | Entregável |
|--------|------|---------|------------|
| **1** | M2.1 | 3d | Schemas e modelos de dados |
| **1-2** | M2.2 | 5d | CRUD de atividades |
| **2-3** | M2.3 | 7d | Upload evidências + S3 |
| **3-4** | M2.4 | 10d | PWA offline + sync |
| **4** | M2.5 | 5d | Captura mídia + geotag |
| **5** | M2.6 | 7d | Relatório EVD01 PDF/A-1 |
| **5-6** | M2.7 | 5d | Testes E2E |
| **6** | M2.8 | 3d | Documentação |

**Total**: ~45 dias úteis (6-7 semanas)

---

## 🏗️ Arquitetura M2

```
┌─────────────────────────────────────────────────────┐
│              PWA (React + Service Worker)           │
│  - IndexedDB (atividades, evidencias_pendentes)    │
│  - Sync Engine (backoff, retry, LWW)               │
│  - CameraCapture (geotag, watermark, compress)     │
└──────────────────┬──────────────────────────────────┘
                   │ HTTPS + Bearer Token
                   │
    ┌──────────────┴───────────────┐
    │                              │
┌───▼──────────┐          ┌────────▼─────────┐
│  Campo API   │          │  Relatórios API  │
│  Port 8001   │          │  Port 8002       │
│              │          │                  │
│ - Atividades │          │ - EVD01 PDF/A-1  │
│ - Evidências │          │ - Merkle Tree    │
│ - Presigned  │          │ - Miniaturas     │
└──────┬───────┘          └──────────────────┘
       │
       │
┌──────▼──────────────────────────┐
│   PostgreSQL + TimescaleDB      │
│                                 │
│ Tables:                         │
│ - atividade                     │
│ - evidencia                     │
│ - sync_log                      │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│         MinIO / S3              │
│                                 │
│ Buckets:                        │
│ - evidencias/                   │
│   - fotos/                      │
│   - videos/                     │
│   - documentos/                 │
└─────────────────────────────────┘
```

---

## 🔐 Segurança M2

### Autenticação e Autorização

- **Token JWT**: Keycloak OIDC (mesmo do M1)
- **Roles**:
  - `CAMPO`: Criar/editar atividades próprias
  - `GESTOR`: Ver/editar todas, cancelar, gerar relatórios
  - `ADMIN`: Full access

### Upload de Evidências

- **Presigned URLs**: Validade 5 minutos
- **Content-Type**: Apenas image/jpeg, image/png, video/mp4
- **Max Size**: 50MB por arquivo
- **Virus Scan**: Integração com ClamAV (opcional M3)

### Hash e Integridade

- **SHA-256**: Calculado no cliente e servidor
- **Merkle Tree**: Root hash no relatório EVD01
- **Watermark**: Timestamp + usuário (não removível)

---

## 📊 Métricas e SLAs M2

### Performance

| Métrica | Target | Medição |
|---------|--------|---------|
| Criar atividade (online) | p95 < 500ms | Timer HTTP |
| Upload evidência (50MB) | p95 < 10s | Presigned URL |
| Sync offline → online | p95 < 5s | Background sync |
| Gerar EVD01 (10 fotos) | p95 < 8s | Timer PDF |

### Disponibilidade

- **Uptime**: 99.5% (excluindo manutenções)
- **RTO**: 15 minutos (Recovery Time Objective)
- **RPO**: 5 minutos (Recovery Point Objective)

### Offline

- **Max tempo offline**: 7 dias
- **Max atividades offline**: 100
- **Max evidências pendentes**: 500

---

## 🧪 Estratégia de Testes M2

### Pirâmide de Testes

```
         ┌─────────┐
         │   E2E   │  5 cenários
         │   (5%)  │
       ┌─┴─────────┴─┐
       │ Integração  │  30 testes
       │    (25%)    │
     ┌─┴─────────────┴─┐
     │    Unitários    │  120 testes
     │     (70%)       │
     └─────────────────┘
```

### Tipos de Testes

1. **Unitários** (120)
   - Schemas Pydantic
   - Validações de estado
   - Cálculo de hashes
   - Merkle tree

2. **Integração** (30)
   - CRUD de atividades
   - Upload com presigned URL
   - Sync offline → online
   - Geração de PDFs

3. **E2E** (5)
   - Fluxo completo online
   - Fluxo completo offline
   - Conflitos e retries
   - Relatório EVD01

### Cobertura

- **Target**: ≥ 80%
- **Ferramentas**: pytest-cov, Playwright
- **CI/CD**: Testes automatizados no PR

---

## 🚧 Riscos e Mitigações M2

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| IndexedDB incompatível em alguns browsers | Média | Alto | Fallback para LocalStorage |
| Presigned URLs expiram antes do upload | Baixa | Médio | Refresh automático |
| Conflitos LWW perdem dados | Média | Alto | Log de conflitos + UI de alerta |
| Upload > 50MB trava mobile | Baixa | Médio | Compressão client-side obrigatória |
| Merkle tree complexo demais | Baixa | Baixo | Usar biblioteca pronta (hashlib) |

---

## ✅ Critérios de Saída M2 (DoD)

### Funcionalidades

- [x] Campo API com CRUD de atividades
- [x] Upload de evidências via S3
- [x] PWA funciona 100% offline
- [x] Sincronização resiliente com retry
- [x] Relatório EVD01 com Merkle tree
- [x] Geotag e watermark em fotos

### Qualidade

- [x] 155 testes (120 unit + 30 int + 5 e2e)
- [x] Cobertura ≥ 80%
- [x] Performance dentro dos SLAs
- [x] Zero bugs críticos

### Documentação

- [x] OpenAPI M2 completo
- [x] Guia PWA offline
- [x] Guia Campo API
- [x] Exemplos práticos

### Infraestrutura

- [x] Bucket S3 configurado
- [x] Service Worker registrado
- [x] IndexedDB funcional
- [x] Logs e métricas expostos

---

## 📝 Próximos Passos

1. **Aprovação do Plano** (Stakeholders)
2. **Provisionamento** (Bucket S3, tabelas DB)
3. **Kickoff M2** (Sprint Planning)
4. **Desenvolvimento Iterativo** (Sprints de 1 semana)
5. **Validação e Homologação**
6. **Deploy em Produção**

---

## 📚 Referências

- [PWA Offline Strategies](https://web.dev/offline-cookbook/)
- [Merkle Tree Implementation](https://brilliant.org/wiki/merkle-tree/)
- [S3 Presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)

---

**Responsável**: TechDengue Team  
**Revisão**: Semanal (sextas-feiras)  
**Status**: 🟡 Aguardando aprovação
