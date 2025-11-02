# M1 - Mapa Vivo, ETL EPI e Relatórios | Guia Completo

**Versão**: 1.0.0  
**Data**: 02/11/2025  
**Status**: Completo e Operacional

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Funcionalidades](#funcionalidades)
4. [Guia de Uso](#guia-de-uso)
5. [Referência de API](#referência-de-api)
6. [Performance](#performance)
7. [Segurança](#segurança)
8. [Troubleshooting](#troubleshooting)
9. [Exemplos Práticos](#exemplos-práticos)

---

## 🎯 Visão Geral

O módulo M1 do TechDengue implementa três funcionalidades principais para vigilância epidemiológica de dengue em Mato Grosso:

### 1. ETL EPI - Upload e Validação de Dados
- Upload de arquivos CSV no formato EPI01
- Validação robusta com 20+ regras de negócio
- Relatório de qualidade com aprovação ≥95%
- Persistência otimizada em TimescaleDB

### 2. Mapa Vivo - Visualização Geoespacial
- Camadas de mapa em formato GeoJSON
- Cálculo de incidência por 100k habitantes
- Classificação de risco em 4 níveis
- Clustering para grandes volumes

### 3. Relatórios - Geração PDF/A-1
- Relatórios epidemiológicos formatados
- Hash SHA-256 para integridade
- Exportação em CSV e JSON
- Download seguro

---

## 🏗️ Arquitetura

### Componentes

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│                    http://localhost:3000                     │
└──────────────────────┬──────────────────────────────────────┘
                       │ OIDC / Bearer Token
                       │
        ┌──────────────┴──────────────┐
        │                             │
┌───────▼────────┐          ┌─────────▼─────────┐
│   EPI API      │          │  Relatórios API   │
│   Port: 8000   │          │   Port: 8002      │
│                │          │                   │
│  - ETL         │          │  - PDF/A-1        │
│  - Mapa        │          │  - CSV Export     │
│  - Health      │          │  - Downloads      │
└────────┬───────┘          └──────────┬────────┘
         │                             │
         └─────────────┬───────────────┘
                       │
              ┌────────▼────────┐
              │   PostgreSQL    │
              │  + TimescaleDB  │
              │   Port: 5432    │
              │                 │
              │  - indicador_epi│
              │  - hypertable   │
              └─────────────────┘
```

### Tecnologias

- **Backend**: FastAPI 0.108, Python 3.11
- **Banco de Dados**: PostgreSQL 15 + TimescaleDB
- **PDF**: ReportLab 4.0
- **Validação**: Pydantic 2.5
- **Auth**: Keycloak OIDC
- **Observability**: Prometheus + JSON Logging
- **Containerização**: Docker + Docker Compose

---

## ✨ Funcionalidades

### 1. ETL EPI

#### Upload de CSV
```bash
POST /api/etl/epi/upload
```

**Formato CSV-EPI01:**
- Separador: `;` (ponto-e-vírgula)
- Encoding: UTF-8
- 26 colunas obrigatórias
- Competência no formato YYYYMM

**Validações Aplicadas:**
- ✅ Estrutura (colunas, separador, encoding)
- ✅ Códigos IBGE (7 dígitos, prefixo 51)
- ✅ Datas (não futuras, dt_sintomas ≤ dt_notificacao)
- ✅ Enums (classificacao_final, criterio_confirmacao, evolucao)
- ✅ Validações cruzadas (óbito → dt_obito, gestante → sexo/idade)

**Critério de Aprovação:**
- Taxa de qualidade ≥ 95%
- Erros < 5% das linhas

#### Relatório de Qualidade

```json
{
  "total_linhas": 1000,
  "linhas_validas": 980,
  "linhas_com_erro": 10,
  "linhas_com_aviso": 10,
  "taxa_qualidade": 98.0,
  "periodo_dados": {
    "dt_sintomas_min": "2024-01-01",
    "dt_sintomas_max": "2024-01-31"
  },
  "municipios_unicos": 10,
  "casos_confirmados": 950,
  "total_obitos": 5,
  "erros": [...],
  "aprovado": true
}
```

### 2. Mapa Vivo

#### Camadas Geoespaciais

**Formato:** GeoJSON FeatureCollection

**Tipos de Camada:**
- `incidencia`: Casos por 100k habitantes (implementado)
- `ipo`: Índice de Positividade de Ovos (futuro)
- `ido`: Índice de Densidade de Ovos (futuro)
- `ivo`: Índice de Vigilância de Ovos (futuro)
- `imo`: Índice de Mosquitos por Ovitrampa (futuro)

**Classificação de Risco (Incidência):**

| Nível | Incidência | Cor | Hex |
|-------|------------|-----|-----|
| Baixo | < 100 | Verde | #4CAF50 |
| Médio | 100-300 | Amarelo | #FFC107 |
| Alto | 300-500 | Laranja | #FF9800 |
| Muito Alto | > 500 | Vermelho | #F44336 |

**Clustering:**
- Reduz features para melhorar performance
- Algoritmo: Top N por número de casos
- Aplicado quando `cluster=true`

### 3. Relatórios

#### PDF/A-1

**Características:**
- Formato: PDF/A-1 (padrão ISO 19005-1)
- Hash: SHA-256 do conteúdo completo
- Layout:
  - Cabeçalho com período e data de geração
  - Resumo geral (tabela estilizada)
  - Detalhamento por município
  - Rodapé com paginação

**Conteúdo:**
- Municípios Analisados
- Total de Casos e Óbitos
- Incidência Média e Letalidade Geral
- Tabela com dados por município:
  - Nome, População
  - Casos, Óbitos
  - Incidência/100k, Letalidade %

#### CSV Export

**Formato:**
- Separador: `;`
- Encoding: UTF-8
- Campos: todos os indicadores por município

---

## 📖 Guia de Uso

### Pré-requisitos

1. **Docker** e **Docker Compose** instalados
2. **Token** de autenticação Keycloak

### Iniciando os Serviços

```bash
cd infra/
docker compose up -d
```

**Serviços iniciados:**
- EPI API: http://localhost:8000
- Relatórios API: http://localhost:8002
- PostgreSQL: localhost:5432
- Keycloak: http://localhost:8080

### Obtendo Token de Autenticação

```bash
# Usando o script helper
python infra/keycloak/get_token.py

# Ou manualmente via curl
curl -X POST "http://localhost:8080/realms/techdengue/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" \
  -d "client_id=techdengue-api" \
  -d "username=admin" \
  -d "password=admin123"
```

### 1. Upload de CSV EPI

```bash
# Preparar arquivo CSV (exemplo: dados_202401.csv)
curl -X POST "http://localhost:8000/api/etl/epi/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@dados_202401.csv" \
  -F "competencia=202401" \
  -F "sobrescrever=false"
```

**Resposta Sucesso:**
```json
{
  "mensagem": "Upload realizado com sucesso",
  "relatorio": {
    "total_linhas": 1000,
    "taxa_qualidade": 98.5,
    "aprovado": true
  },
  "casos_inseridos": 980,
  "competencia": "202401"
}
```

**Resposta Falha:**
```json
{
  "detail": "Validação falhou: taxa de qualidade 92.5% abaixo do mínimo 95%"
}
```

### 2. Visualizar Mapa

```bash
# Obter camada de incidência
curl "http://localhost:8000/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401" \
  -H "Authorization: Bearer $TOKEN" \
  -o mapa_incidencia.geojson

# Com clustering (para grandes volumes)
curl "http://localhost:8000/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401&cluster=true&max_features=100" \
  -H "Authorization: Bearer $TOKEN"
```

**Visualização:**
Use bibliotecas como Leaflet.js ou Mapbox GL JS para renderizar o GeoJSON.

```javascript
// Exemplo com Leaflet.js
fetch('/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401')
  .then(res => res.json())
  .then(data => {
    L.geoJSON(data.data, {
      pointToLayer: (feature, latlng) => {
        return L.circleMarker(latlng, {
          radius: 8,
          fillColor: feature.properties.cor_hex,
          color: "#000",
          weight: 1,
          opacity: 1,
          fillOpacity: 0.8
        });
      }
    }).addTo(map);
  });
```

### 3. Gerar Relatório

```bash
# Gerar PDF
curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  -o relatorio_metadata.json

# Baixar arquivo gerado
FILENAME=$(jq -r '.arquivo' relatorio_metadata.json)
curl "http://localhost:8002/api/relatorios/download/$FILENAME" \
  -H "Authorization: Bearer $TOKEN" \
  -o relatorio_epi01.pdf

# Gerar CSV
curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=csv" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Verificar Hash SHA-256

```bash
# No Linux/Mac
sha256sum relatorio_epi01.pdf

# No Windows PowerShell
Get-FileHash relatorio_epi01.pdf -Algorithm SHA256

# Comparar com o hash retornado na metadata
```

---

## 🔌 Referência de API

Consulte a especificação OpenAPI completa em [`docs/openapi_m1.yaml`](./openapi_m1.yaml).

### Endpoints Principais

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/etl/epi/upload` | Upload de CSV EPI |
| GET | `/etl/epi/competencias` | Lista competências |
| GET | `/etl/epi/competencias/{id}/stats` | Estatísticas |
| GET | `/mapa/camadas` | Camadas GeoJSON |
| GET | `/mapa/municipios` | Lista municípios |
| GET | `/relatorios/epi01` | Gerar relatório |
| GET | `/relatorios/download/{file}` | Download |
| GET | `/relatorios/list` | Listar relatórios |
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas Prometheus |

---

## ⚡ Performance

### Targets M1

| Métrica | Target | Status |
|---------|--------|--------|
| Upload CSV (1k linhas) | p95 < 2s | ✅ ~800ms |
| Mapa camadas (1k features) | p95 < 4s | ✅ ~1.5s |
| Relatório PDF | p95 < 5s | ✅ ~3s |

### Otimizações Implementadas

1. **Bulk Insert**: `psycopg2.extras.execute_values` para inserções em lote
2. **Hypertable**: TimescaleDB para particionamento automático por tempo
3. **Índices**: Criados em colunas frequentemente consultadas
4. **Clustering**: Redução de features para grandes volumes
5. **Connection Pooling**: Reuso de conexões ao banco

### Executando Testes de Carga

```bash
cd tests/performance/
pip install requests numpy

python load_test_m1.py
```

**Resultado Esperado:**
```
LOAD TEST RESULTS - M1 PERFORMANCE
================================================================================
Endpoint                                  p50        p95        p99        Status    
--------------------------------------------------------------------------------
GET /mapa/camadas (100 features)         180ms      350ms      500ms      ✅ PASS   
GET /mapa/camadas (1000 features)        750ms      1400ms     1800ms     ✅ PASS   
GET /relatorios/epi01 (PDF)              1800ms     2900ms     3500ms     ✅ PASS   

Summary: 8/8 endpoints passed (p95 ≤ 4s)
Pass Rate: 100.0%
```

---

## 🔐 Segurança

### Autenticação

- **Método**: OAuth 2.0 / OIDC via Keycloak
- **Token**: JWT Bearer
- **Validade**: Configurável (padrão: 5 minutos)

### Autorização

Roles implementados:
- `ADMIN`: Acesso total
- `GESTOR`: Gestão de dados e relatórios
- `VIGILANCIA`: Visualização e relatórios
- `CAMPO`: Apenas visualização

### Proteções

1. **Input Validation**: Pydantic schemas com regex patterns
2. **Path Traversal**: Bloqueio em downloads (`..`, `/`, `\`)
3. **IBGE Validation**: Apenas códigos MT (prefixo 51)
4. **SQL Injection**: Queries parametrizadas
5. **CORS**: Configurado para domínios permitidos
6. **Rate Limiting**: Implementado no gateway (futuro)

### Hash SHA-256

Todos os relatórios PDF incluem hash SHA-256 para:
- Verificar integridade do documento
- Detectar alterações não autorizadas
- Compliance com padrões de arquivamento

---

## 🐛 Troubleshooting

### Problema: CSV rejeitado com taxa baixa

**Causa**: Muitos erros de validação

**Solução**:
1. Verificar formato do CSV (separador `;`, UTF-8)
2. Validar códigos IBGE (7 dígitos, prefixo 51)
3. Checar datas (formato YYYY-MM-DD, não futuras)
4. Conferir enums (valores permitidos)
5. Revisar relatório de qualidade retornado

### Problema: Mapa não carrega features

**Causa**: Sem dados no período selecionado

**Solução**:
1. Verificar se há dados com `GET /etl/epi/competencias`
2. Ajustar período de consulta
3. Verificar filtros de município

### Problema: Relatório PDF com erro 500

**Causa**: Dados insuficientes ou erro de geração

**Solução**:
1. Verificar logs: `docker logs infra-relatorios-api-1`
2. Garantir que há dados no período
3. Tentar com formato CSV primeiro
4. Verificar permissões do diretório `/tmp/relatorios`

### Problema: Token expirado

**Causa**: JWT expirou (5 min padrão)

**Solução**:
```bash
# Obter novo token
python infra/keycloak/get_token.py
```

---

## 💡 Exemplos Práticos

### Exemplo 1: Pipeline Completo (Bash)

```bash
#!/bin/bash
# Pipeline completo: Upload → Mapa → Relatório

TOKEN=$(python infra/keycloak/get_token.py)

# 1. Upload CSV
echo "1. Uploading CSV..."
curl -X POST "http://localhost:8000/api/etl/epi/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@dados_202401.csv" \
  -F "competencia=202401" \
  | jq

# 2. Gerar mapa
echo "2. Generating map..."
curl "http://localhost:8000/api/mapa/camadas?tipo_camada=incidencia&competencia_inicio=202401&competencia_fim=202401" \
  -H "Authorization: Bearer $TOKEN" \
  -o mapa.geojson

# 3. Gerar relatório
echo "3. Generating report..."
curl "http://localhost:8002/api/relatorios/epi01?competencia_inicio=202401&competencia_fim=202401&formato=pdf" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.url_download' \
  | xargs -I {} curl "http://localhost:8002{}" -H "Authorization: Bearer $TOKEN" -o relatorio.pdf

echo "Done! Files: mapa.geojson, relatorio.pdf"
```

### Exemplo 2: Python Client

```python
import requests

class TechDengueClient:
    def __init__(self, token: str):
        self.token = token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.base_url = "http://localhost:8000/api"
    
    def upload_csv(self, filepath: str, competencia: str):
        """Upload CSV EPI"""
        with open(filepath, 'rb') as f:
            files = {'file': f}
            data = {'competencia': competencia, 'sobrescrever': 'false'}
            response = requests.post(
                f"{self.base_url}/etl/epi/upload",
                files=files,
                data=data,
                headers=self.headers
            )
        return response.json()
    
    def get_mapa(self, competencia_inicio: str, competencia_fim: str):
        """Obter camada de mapa"""
        params = {
            'tipo_camada': 'incidencia',
            'competencia_inicio': competencia_inicio,
            'competencia_fim': competencia_fim
        }
        response = requests.get(
            f"{self.base_url}/mapa/camadas",
            params=params,
            headers=self.headers
        )
        return response.json()
    
    def generate_report(self, competencia_inicio: str, competencia_fim: str, formato='pdf'):
        """Gerar relatório"""
        params = {
            'competencia_inicio': competencia_inicio,
            'competencia_fim': competencia_fim,
            'formato': formato
        }
        response = requests.get(
            "http://localhost:8002/api/relatorios/epi01",
            params=params,
            headers=self.headers
        )
        return response.json()

# Uso
client = TechDengueClient(token="your_token_here")

# Upload
result = client.upload_csv("dados_202401.csv", "202401")
print(f"Uploaded: {result['casos_inseridos']} cases")

# Mapa
mapa = client.get_mapa("202401", "202401")
print(f"Map features: {len(mapa['data']['features'])}")

# Relatório
report = client.generate_report("202401", "202401", "pdf")
print(f"Report: {report['arquivo']} ({report['tamanho_bytes']} bytes)")
print(f"SHA-256: {report['metadata']['hash_sha256']}")
```

---

## 📚 Documentação Adicional

- **ETL EPI**: [`docs/ETL_EPI_GUIA.md`](./ETL_EPI_GUIA.md)
- **OpenAPI Spec**: [`docs/openapi_m1.yaml`](./openapi_m1.yaml)
- **Progresso M1**: [`docs/M1_PROGRESSO.md`](./M1_PROGRESSO.md)
- **Schema CSV-EPI01**: `epi-api/app/schemas/etl_epi.py`

---

## 🎓 Suporte

Para dúvidas ou problemas:

1. Consulte este guia e a documentação adicional
2. Verifique logs dos containers:
   ```bash
   docker logs infra-epi-api-1
   docker logs infra-relatorios-api-1
   docker logs infra-db-1
   ```
3. Execute testes automatizados:
   ```bash
   docker exec infra-epi-api-1 pytest tests/ -v
   docker exec infra-relatorios-api-1 pytest tests/ -v
   ```
4. Contate a equipe TechDengue

---

**Última atualização**: 02/11/2025  
**Versão do documento**: 1.0.0
