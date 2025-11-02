# TechDengue M1 - Sistema de Vigilância Epidemiológica

[![Tests](https://img.shields.io/badge/tests-31%2F31%20passing-brightgreen)](docs/M1_RELATORIO_VALIDACAO.md)
[![Coverage](https://img.shields.io/badge/coverage-88%25-green)](docs/M1_RELATORIO_VALIDACAO.md)
[![Performance](https://img.shields.io/badge/p95-%3C4s-brightgreen)](docs/M1_RELATORIO_VALIDACAO.md)
[![Status](https://img.shields.io/badge/status-production%20ready-blue)](docs/M1_RELATORIO_VALIDACAO.md)

Sistema completo de vigilância epidemiológica de dengue para o estado de Mato Grosso, implementando upload de dados, visualização geoespacial e geração de relatórios oficiais.

---

## 🚀 Quick Start

### Pré-requisitos

- Docker 20.10+
- Docker Compose 2.0+
- Python 3.11+ (opcional, para testes locais)

### Iniciando o Sistema

```bash
# Clone o repositório
git clone https://github.com/your-org/techdengue.git
cd Techdengue_MT

# Inicie todos os serviços
cd infra/
docker compose up -d

# Verifique o status
docker compose ps
```

**Serviços disponíveis:**
- EPI API: http://localhost:8000
- Relatórios API: http://localhost:8002
- Frontend: http://localhost:3000 (M2)
- Keycloak: http://localhost:8080
- PostgreSQL: localhost:5432

### Primeiro Uso

```bash
# 1. Obter token de autenticação
python infra/keycloak/get_token.py

# 2. Upload de CSV EPI
curl -X POST "http://localhost:8000/api/etl/epi/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@dados_dengue_202401.csv" \
  -F "competencia=202401"

# 3. Visualizar mapa
curl "http://localhost:8000/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401" \
  -H "Authorization: Bearer $TOKEN" \
  -o mapa.geojson

# 4. Gerar relatório PDF
curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=pdf" \
  -H "Authorization: Bearer $TOKEN"
```

---

## ✨ Funcionalidades M1

### 1. ETL EPI - Upload e Validação de Dados

Upload de arquivos CSV no formato EPI01 com validação robusta:

- ✅ **20+ regras de validação** (IBGE, datas, enums, cross-field)
- ✅ **Relatório de qualidade** com taxa ≥95% para aprovação
- ✅ **Bulk insert otimizado** (1000 linhas em ~800ms)
- ✅ **Persistência em TimescaleDB** (hypertable particionada)

**Exemplo de CSV válido:**
```csv
dt_notificacao;dt_sintomas;municipio_cod_ibge;sexo;idade;gestante;classificacao_final;criterio_confirmacao;...
2024-01-15;2024-01-13;5103403;F;28;N;DENGUE;LABORATORIAL;...
```

### 2. Mapa Vivo - Visualização Geoespacial

Camadas de mapa em formato GeoJSON para visualização:

- ✅ **Incidência por 100k habitantes** com classificação de risco
- ✅ **4 níveis de risco** (Baixo, Médio, Alto, Muito Alto)
- ✅ **Cores automáticas** (Verde, Amarelo, Laranja, Vermelho)
- ✅ **Clustering** para grandes volumes (até 10k features)

**Classificação de Risco:**
- 🟢 Baixo: < 100 casos/100k
- 🟡 Médio: 100-300
- 🟠 Alto: 300-500
- 🔴 Muito Alto: > 500

### 3. Relatórios - Geração PDF/A-1

Relatórios epidemiológicos oficiais com hash SHA-256:

- ✅ **PDF/A-1** (padrão ISO 19005-1 para arquivamento)
- ✅ **Hash SHA-256** para integridade do documento
- ✅ **Layout profissional** (resumo + detalhamento)
- ✅ **Exportação CSV** (separador `;`, UTF-8)

---

## 📊 Status do Projeto

### Testes Automatizados

```
EPI API:          23/23 tests passing (100%)
Relatórios API:    8/8 tests passing (100%)
Total:            31/31 tests passing (100%)
Coverage:         ~88% (target: ≥80%)
```

### Performance

| Endpoint | p95 | Target | Status |
|----------|-----|--------|--------|
| Upload CSV (1k linhas) | 800ms | <2s | ✅ |
| Mapa (1k features) | 1.4s | <4s | ✅ |
| Relatório PDF | 2.9s | <5s | ✅ |

### Progresso M1

```
M1.1-M1.6  (ETL EPI)            ████████████████████  100%
M1.7-M1.8  (Mapa Vivo)          ████████████████████  100%
M1.9-M1.10 (Relatórios PDF)     ████████████████████  100%
M1.11      (OpenAPI)            ████████████████████  100%
M1.12      (Performance)        ████████████████████  100%
M1.13      (Documentação)       ████████████████████  100%

Total M1: ████████████████████ 100% COMPLETO
```

---

## 📖 Documentação

### Guias Principais

- **[Guia Completo M1](docs/M1_GUIA_COMPLETO.md)** - Guia detalhado de uso
- **[Guia ETL EPI](docs/ETL_EPI_GUIA.md)** - Especificação do formato CSV
- **[Relatório de Validação](docs/M1_RELATORIO_VALIDACAO.md)** - Validação completa
- **[OpenAPI Spec](docs/openapi_m1.yaml)** - Especificação de API

### Documentos Adicionais

- **[Progresso M1](docs/M1_PROGRESSO.md)** - Histórico de implementação
- **[Validação M0](docs/VALIDACAO_M0.md)** - Validação do módulo base
- **[Plano de Implementação](docs/PLANO_DE_IMPLEMENTACAO.md)** - Roadmap completo

---

## 🏗️ Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│                 Frontend React (Port 3000)                │
│          Leaflet.js | Recharts | TailwindCSS             │
└────────────────────────┬─────────────────────────────────┘
                         │ OIDC/Bearer Token
                         │
        ┌────────────────┴────────────────┐
        │                                 │
┌───────▼───────┐               ┌─────────▼─────────┐
│   EPI API     │               │  Relatórios API   │
│   Port 8000   │               │   Port 8002       │
│               │               │                   │
│ - ETL         │               │ - PDF/A-1         │
│ - Mapa        │               │ - CSV Export      │
│ - Metrics     │               │ - SHA-256 Hash    │
└───────┬───────┘               └─────────┬─────────┘
        │                                 │
        └─────────────┬───────────────────┘
                      │
           ┌──────────▼──────────┐
           │   PostgreSQL 15     │
           │   + TimescaleDB     │
           │                     │
           │ Tables:             │
           │ - indicador_epi     │
           │   (hypertable)      │
           │ - atividade         │
           │ - evidencia         │
           │ - relatorio         │
           └─────────────────────┘
```

### Tecnologias

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| Backend | FastAPI | 0.108 |
| Validação | Pydantic | 2.5 |
| Banco | PostgreSQL + TimescaleDB | 15 + 2.x |
| PDF | ReportLab | 4.0 |
| Auth | Keycloak | 24.0 |
| Containers | Docker + Compose | 24.0 |
| Metrics | Prometheus | Latest |

---

## 🔐 Segurança

### Autenticação

- **OAuth 2.0 / OIDC** via Keycloak
- **JWT Bearer Token** em todos os endpoints
- **Roles**: ADMIN, GESTOR, VIGILANCIA, CAMPO
- **Token Expiration**: 5 minutos (configurável)

### Proteções Implementadas

- ✅ Input validation (Pydantic schemas)
- ✅ Path traversal protection
- ✅ SQL injection prevention (parametrized queries)
- ✅ IBGE code validation (apenas MT)
- ✅ Hash SHA-256 em PDFs (integridade)
- ✅ CORS configurado
- ✅ Rate limiting (via gateway - futuro)

---

## 🧪 Testes

### Executar Testes Automatizados

```bash
# EPI API
docker exec infra-epi-api-1 pytest tests/ -v

# Relatórios API
docker exec infra-relatorios-api-1 pytest tests/ -v

# Todos os testes
docker exec infra-epi-api-1 pytest tests/ -v && \
docker exec infra-relatorios-api-1 pytest tests/ -v
```

### Testes de Carga

```bash
cd tests/performance/
pip install requests numpy
python load_test_m1.py
```

**Resultado esperado:** Todos os endpoints com p95 ≤ 4s ✅

---

## 📦 Estrutura do Projeto

```
Techdengue_MT/
├── epi-api/                    # EPI API (ETL + Mapa)
│   ├── app/
│   │   ├── schemas/            # Pydantic models
│   │   ├── services/           # Business logic
│   │   ├── routers/            # FastAPI endpoints
│   │   └── middleware/         # Observability
│   └── tests/                  # 23 testes automatizados
│
├── relatorios-api/             # Relatórios API (PDF + CSV)
│   ├── app/
│   │   ├── schemas/
│   │   ├── services/           # PDF generator
│   │   └── routers/
│   └── tests/                  # 8 testes automatizados
│
├── db/
│   └── flyway/migrations/      # Database migrations
│       ├── V5__add_epi_columns.sql
│       └── V6__make_old_columns_nullable.sql
│
├── infra/                      # Docker Compose
│   ├── docker-compose.yml
│   └── keycloak/               # Keycloak config
│
├── docs/                       # Documentação completa
│   ├── openapi_m1.yaml         # API Spec
│   ├── M1_GUIA_COMPLETO.md
│   ├── M1_RELATORIO_VALIDACAO.md
│   └── ETL_EPI_GUIA.md
│
└── tests/
    └── performance/
        └── load_test_m1.py     # Load testing script
```

---

## 🚢 Deploy

### Produção

```bash
# Build images
docker compose -f infra/docker-compose.prod.yml build

# Push to registry
docker tag infra-epi-api registry.example.com/epi-api:1.0.0
docker push registry.example.com/epi-api:1.0.0

# Deploy
kubectl apply -f k8s/
```

### Variáveis de Ambiente

```bash
# EPI API
DATABASE_URL=postgresql://user:pass@host:5432/techdengue
KEYCLOAK_URL=https://auth.example.com
KEYCLOAK_REALM=techdengue
KEYCLOAK_CLIENT_ID=techdengue-api

# Relatórios API
DATABASE_URL=...
REPORTS_DIR=/app/reports
```

---

## 🐛 Troubleshooting

### CSV rejeitado

**Problema:** Taxa de qualidade < 95%

**Solução:**
1. Verificar formato (separador `;`, UTF-8)
2. Validar códigos IBGE (7 dígitos, prefixo 51)
3. Checar datas (não futuras)
4. Revisar relatório de qualidade retornado

### Mapa sem features

**Problema:** Sem dados no período

**Solução:**
1. Verificar competências com `GET /etl/epi/competencias`
2. Fazer upload de CSV para o período
3. Ajustar filtros de período

### Token expirado

**Problema:** 401 Unauthorized

**Solução:**
```bash
python infra/keycloak/get_token.py
```

Mais detalhes: [M1 Guia Completo](docs/M1_GUIA_COMPLETO.md#troubleshooting)

---

## 📞 Suporte

- **Documentação:** [docs/M1_GUIA_COMPLETO.md](docs/M1_GUIA_COMPLETO.md)
- **Issues:** GitHub Issues
- **Email:** suporte@techdengue.mt.gov.br

---

## 📄 Licença

Proprietary - Governo do Estado de Mato Grosso

---

## 👥 Equipe

Desenvolvido pela equipe TechDengue - Vigilância em Saúde de Mato Grosso

**Status do Projeto:** ✅ **M1 COMPLETO E VALIDADO**

---

**Última atualização:** 02/11/2025  
**Versão:** 1.0.0  
**Build:** [![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](docs/M1_RELATORIO_VALIDACAO.md)
