# Hardening e Segurança - TechDengue MT

## 📊 Visão Geral

Suite completa de **hardening de segurança** com rate limiting, security headers, audit logs e rotas LIRAa preparadas para dados futuros.

**Status**: ✅ **100% COMPLETO** | Production Ready  
**Data**: 2024-11-02  
**Versão**: 1.0.0

---

## 🎯 Objetivos Alcançados

- ✅ **Rate Limiting** (60 req/min em produção)
- ✅ **Security Headers** (CSP, HSTS, XSS Protection)
- ✅ **Audit Logging** (todas operações sensíveis)
- ✅ **CORS** configurado (whitelist de origens)
- ✅ **Request ID** tracking
- ✅ **Rotas LIRAa** (IPO/IDO/IVO/IMO) preparadas

---

## 📦 Componentes Implementados

### 1. Rate Limiting Middleware

**Arquivo**: `epi-api/app/middleware/security.py` (200 linhas)

#### Features

- **Token Bucket Algorithm**: Controle de requisições por minuto
- **Identificação**: Por user_id (autenticado) ou IP
- **Response Headers**: X-RateLimit-Limit, Remaining, Reset
- **Configurável por Ambiente**:
  - Production: 60 req/min
  - Staging: 120 req/min
  - Development: 1000 req/min

#### Uso

```python
from app.middleware.security import RateLimitMiddleware

app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

#### Response Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699123456
```

#### Error Response (429)

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

**Headers**:
- `Retry-After: 60` (segundos)

---

### 2. Security Headers Middleware

**Arquivo**: `epi-api/app/middleware/security.py`

#### Headers Aplicados

| Header | Value | Proteção |
|--------|-------|----------|
| **X-Content-Type-Options** | nosniff | Previne MIME sniffing |
| **X-Frame-Options** | DENY | Previne clickjacking |
| **X-XSS-Protection** | 1; mode=block | Ativa filtro XSS |
| **Strict-Transport-Security** | max-age=31536000 | Força HTTPS |
| **Referrer-Policy** | strict-origin-when-cross-origin | Controla referrer |
| **Permissions-Policy** | geolocation=(), microphone=() | Bloqueia APIs |
| **Content-Security-Policy** | default-src 'self'... | Previne XSS/injection |

#### Content Security Policy (CSP)

```
default-src 'self';
script-src 'self' 'unsafe-inline' 'unsafe-eval';
style-src 'self' 'unsafe-inline';
img-src 'self' data: https:;
font-src 'self' data:;
connect-src 'self' https://keycloak.techdengue.mt.gov.br
```

#### Headers Removidos

- `Server`
- `X-Powered-By`

---

### 3. CORS Configuration

**Arquivo**: `epi-api/app/middleware/security.py`

#### Origens Permitidas

```python
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "https://techdengue.mt.gov.br",
    "https://app.techdengue.mt.gov.br",
]
```

#### Configuração

```python
CORSMiddleware(
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    expose_headers=["X-RateLimit-*", "X-Total-Count", "X-File-Hash"],
    max_age=3600,
)
```

---

### 4. Request ID Middleware

**Arquivo**: `epi-api/app/middleware/security.py`

#### Features

- **UUID único** para cada requisição
- **Header**: `X-Request-ID`
- **Propagação**: Do request ao response
- **Logging**: Incluído em todos os logs

#### Exemplo

```bash
# Request
curl -H "X-Request-ID: 123e4567-e89b-12d3-a456-426614174000" \
  http://localhost:8000/api/indicadores/kpis

# Response
HTTP/1.1 200 OK
X-Request-ID: 123e4567-e89b-12d3-a456-426614174000
```

---

### 5. Audit Logging

**Arquivo**: `epi-api/app/middleware/audit.py` (200 linhas)

#### O Que É Auditado

**Sempre auditado**:
- Endpoints sensíveis: `/api/etl/`, `/api/relatorios/`, `/api/admin/`
- Write operations: POST, PUT, DELETE, PATCH

**Não auditado**:
- Health checks: `/health`, `/metrics`
- Documentação: `/docs`, `/openapi.json`

#### Log Entry Format (JSON)

```json
{
  "timestamp": "2024-11-02T17:30:00Z",
  "request_id": "abc123",
  "user_id": "user_456",
  "user_email": "analista@saude.mt.gov.br",
  "client_ip": "192.168.1.100",
  "method": "POST",
  "path": "/api/etl/sinan/import",
  "query_params": {"ano": "2024"},
  "status_code": 202,
  "process_time_ms": 1234.56,
  "user_agent": "Mozilla/5.0...",
  "request_data": {
    "arquivo_csv": "/data/sinan_2024.csv",
    "doenca_tipo": "DENGUE"
  }
}
```

#### Sanitização de Dados

Campos sensíveis são redacted:
- `password`
- `token`
- `secret`
- `api_key`
- `access_token`

**Exemplo**:
```json
{
  "username": "user@example.com",
  "password": "***REDACTED***"
}
```

#### Log Rotation

```python
RotatingFileHandler(
    filename="/var/log/techdengue/audit.log",
    maxBytes=100 * 1024 * 1024,  # 100 MB
    backupCount=10,
    encoding="utf-8",
)
```

#### Operações Críticas

Operações críticas são **também salvas em banco** (para consulta futura):
- `/api/admin/*`
- `/api/etl/sinan/import`
- `/api/users/delete`

---

### 6. Rotas LIRAa (IPO/IDO/IVO/IMO)

**Arquivos**:
- `epi-api/app/schemas/liraa.py` (220 linhas)
- `epi-api/app/routers/liraa.py` (250 linhas)

#### Índices Implementados

| Índice | Nome Completo | Descrição |
|--------|---------------|-----------|
| **IPO** | Índice de Pendências | % de imóveis com pendências |
| **IDO** | Índice de Depósitos | % de depósitos com larvas |
| **IVO** | Índice de Vetores | % de imóveis com vetores |
| **IMO** | Índice de Mosquitos | % de imóveis com mosquitos adultos |

#### Classificação de Risco

| Classificação | Faixa | Cor |
|---------------|-------|-----|
| **SATISFATÓRIO** | < 1% | 🟢 Verde |
| **ALERTA** | 1% a 3.9% | 🟡 Amarelo |
| **RISCO** | ≥ 4% | 🔴 Vermelho |

#### Endpoints Preparados

##### GET /api/liraa/indices

Retorna índices agregados por município.

```bash
curl "http://localhost:8000/api/liraa/indices?ano=2024&tipo_indice=IPO"
```

**Response**:
```json
{
  "ano": 2024,
  "total_municipios": 141,
  "indices": [
    {
      "codigo_ibge": "5103403",
      "municipio": "Cuiabá",
      "tipo_indice": "IPO",
      "valor": 2.5,
      "classificacao": "ALERTA",
      "imoveis_inspecionados": 5000,
      "imoveis_positivos": 125,
      "data_levantamento": "2024-10-15",
      "semana_epi": 42
    }
  ]
}
```

##### GET /api/liraa/series-temporais

Série temporal de índices.

```bash
curl "http://localhost:8000/api/liraa/series-temporais?ano=2024&tipo_indice=IPO&codigo_ibge=5103403"
```

##### GET /api/liraa/ranking

Ranking de municípios por índice.

```bash
curl "http://localhost:8000/api/liraa/ranking?ano=2024&tipo_indice=IPO&limite=10&ordem=desc"
```

##### GET /api/liraa/comparativo

Compara índices entre dois períodos.

```bash
curl "http://localhost:8000/api/liraa/comparativo?tipo_indice=IPO&ano1=2023&semana1=1&ano2=2024&semana2=1"
```

##### GET /api/liraa/mapa

GeoJSON para visualização no mapa.

```bash
curl "http://localhost:8000/api/liraa/mapa?ano=2024&tipo_indice=IPO"
```

**Response (GeoJSON)**:
```json
{
  "type": "FeatureCollection",
  "ano": 2024,
  "tipo_indice": "IPO",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "codigo_ibge": "5103403",
        "nome": "Cuiabá",
        "valor_ipo": 2.5,
        "classificacao_geral": "ALERTA"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [...]
      }
    }
  ]
}
```

##### GET /api/liraa/estatisticas

Estatísticas descritivas.

```bash
curl "http://localhost:8000/api/liraa/estatisticas?ano=2024&tipo_indice=IPO"
```

#### Status Atual

**Nota**: Todas as rotas estão preparadas mas retornam **503 Service Unavailable** até que os datasets LIRAa sejam carregados.

**Mensagem**:
```json
{
  "detail": "Dados LIRAa não disponíveis. Aguardando carregamento de datasets."
}
```

---

## 🔧 Configuração

### 1. Aplicar Middlewares

**Arquivo**: `epi-api/app/main.py`

```python
from app.middleware.security import setup_security_middleware
from app.middleware.audit import AuditLogMiddleware, configure_audit_logger

# Configurar audit logger
configure_audit_logger()

# Setup security
setup_security_middleware(app)

# Audit logging
app.add_middleware(AuditLogMiddleware)
```

### 2. Variáveis de Ambiente

```bash
# .env
ENVIRONMENT=production
LOG_DIR=/var/log/techdengue
ALLOWED_ORIGINS=https://techdengue.mt.gov.br,https://app.techdengue.mt.gov.br
```

---

## 🧪 Testes

### Rate Limiting

```bash
# Testar limite
for i in {1..70}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
    http://localhost:8000/api/indicadores/kpis
done

# Deve retornar 429 após 60 requisições
```

### Security Headers

```bash
curl -I http://localhost:8000/api/indicadores/kpis

# Verificar headers
HTTP/1.1 200 OK
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'...
```

### Audit Logs

```bash
# Fazer operação auditada
curl -X POST http://localhost:8000/api/etl/sinan/import \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"arquivo_csv": "/data/test.csv"}'

# Verificar log
tail -f /var/log/techdengue/audit.log | jq
```

---

## 📊 Métricas de Implementação

```
╔════════════════════════════════════════════════════════════════╗
║         HARDENING & SECURITY - COMPLETO ✅                     ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Security Middleware:       200 linhas        ✅              ║
║  Audit Middleware:          200 linhas        ✅              ║
║  LIRAa Schemas:             220 linhas        ✅              ║
║  LIRAa Router:              250 linhas        ✅              ║
║  Documentação:              400 linhas        ✅              ║
║  ──────────────────────────────────────────                   ║
║  TOTAL:                   1.270 linhas        ✅              ║
╠════════════════════════════════════════════════════════════════╣
║  Middlewares:                4 middlewares    ✅              ║
║  Security Headers:          10 headers        ✅              ║
║  Audit Targets:              3 categorias     ✅              ║
║  Endpoints LIRAa:            6 endpoints      ✅              ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🔜 Quando Dados LIRAa Estiverem Disponíveis

### 1. Criar Tabela no Banco

```sql
CREATE TABLE liraa_indices (
    id SERIAL PRIMARY KEY,
    codigo_ibge VARCHAR(7) NOT NULL,
    tipo_indice VARCHAR(10) NOT NULL,
    valor DECIMAL(5,2) NOT NULL,
    imoveis_inspecionados INT NOT NULL,
    imoveis_positivos INT NOT NULL,
    data_levantamento DATE NOT NULL,
    semana_epi INT NOT NULL,
    ano INT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_liraa_municipio ON liraa_indices(codigo_ibge, ano);
CREATE INDEX idx_liraa_tipo ON liraa_indices(tipo_indice, ano);
```

### 2. Implementar Service

```python
# app/services/liraa_service.py
class LiraaService:
    async def get_indices(self, filtros: LiraaFiltros):
        # Query database
        # Calculate classificacao
        # Return IndiceLiraa objects
        pass
```

### 3. Remover HTTPException 503

Substituir nas rotas:
```python
# De:
raise HTTPException(status_code=503, detail="...")

# Para:
service = LiraaService(db)
return await service.get_indices(filtros)
```

---

## 📚 Referências

**Segurança**:
- OWASP Top 10: <https://owasp.org/www-project-top-ten/>
- CSP Reference: <https://content-security-policy.com/>
- Rate Limiting Patterns: <https://cloud.google.com/architecture/rate-limiting-strategies>

**LIRAa**:
- MS - Diretrizes Nacionais Dengue
- Manual LIRAa: <http://portalms.saude.gov.br/>

---

**Equipe TechDengue MT**  
**Data**: 2024-11-02  
**Versão**: 1.0.0
