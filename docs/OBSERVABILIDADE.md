# Observabilidade - TechDengue

Implementação completa de observabilidade para as APIs do TechDengue, seguindo o Plano de Implementação (M0 - Fundações).

## Stack de Observabilidade

- **Logs**: JSON estruturado com `python-json-logger`
- **Métricas**: Prometheus (`prometheus-client`)
- **Tracing**: OpenTelemetry (instrumentação FastAPI)
- **Correlação**: `X-Request-ID` propagado em todos os requests

## Middlewares Implementados

### 1. RequestIDMiddleware

Gera ou propaga `X-Request-ID` para correlação de requisições.

**Funcionalidades:**
- Captura `X-Request-ID` do header de entrada ou gera novo UUID
- Armazena em `request.state.request_id`
- Adiciona no response header `X-Request-ID`

**Uso:**
```bash
curl -H "X-Request-ID: my-custom-id" http://localhost:8000/api/health
```

### 2. LoggingMiddleware

Logs estruturados JSON com contexto completo.

**Campos logged:**
- `timestamp`: ISO 8601
- `level`: INFO, ERROR, etc.
- `service`: nome da API (epi-api, campo-api, relatorios-api)
- `message`: descrição da requisição
- `request_id`: UUID para correlação
- `method`: HTTP method (GET, POST, etc.)
- `path`: endpoint path
- `status_code`: código de resposta HTTP
- `latency_ms`: tempo de resposta em milissegundos
- `user_id`: (opcional) ID do usuário autenticado
- `error`: (opcional) mensagem de erro

**Exemplo de log:**
```json
{
  "timestamp": "2025-11-02 12:00:00,000",
  "level": "INFO",
  "service": "epi-api",
  "message": "GET /api/health - 200",
  "request_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "method": "GET",
  "path": "/api/health",
  "status_code": 200,
  "latency_ms": 15.42
}
```

### 3. MetricsMiddleware

Coleta métricas Prometheus para análise de performance e SLOs.

**Métricas expostas:**

| Métrica | Tipo | Descrição | Labels |
|---------|------|-----------|---------|
| `http_requests_total` | Counter | Total de requisições HTTP | method, endpoint, status |
| `http_request_duration_seconds` | Histogram | Latência de requisições | method, endpoint |
| `http_requests_in_progress` | Gauge | Requisições em andamento | method, endpoint |
| `http_errors_total` | Counter | Total de erros HTTP | method, endpoint, status |

**Buckets de latência (histogram):**
- 10ms, 50ms, 100ms, 500ms, 1s, 2.5s, 5s, 10s

**Path normalization:**
- IDs numéricos e UUIDs são substituídos por `{id}`
- Exemplo: `/atividades/123` → `/atividades/{id}`
- Permite agregação por endpoint sem explosão de cardinalidade

## Endpoints de Observabilidade

### Health Check

```bash
GET /api/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "epi-api",
  "version": "1.0.0"
}
```

### Metrics (Prometheus)

```bash
GET /metrics
```

**Response:** Formato Prometheus text

```prometheus
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{endpoint="/api/health",method="GET",status="200"} 42.0

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{endpoint="/api/health",method="GET",le="0.01"} 35.0
http_request_duration_seconds_bucket{endpoint="/api/health",method="GET",le="0.05"} 40.0
...
```

## Configuração de Coleta

### Prometheus

**prometheus.yml:**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'epi-api'
    static_configs:
      - targets: ['epi-api:8000']
    metrics_path: '/metrics'

  - job_name: 'campo-api'
    static_configs:
      - targets: ['campo-api:8001']
    metrics_path: '/metrics'

  - job_name: 'relatorios-api'
    static_configs:
      - targets: ['relatorios-api:8002']
    metrics_path: '/metrics'
```

### Grafana Dashboards

**Métricas recomendadas:**

1. **Request Rate**
   ```promql
   rate(http_requests_total[5m])
   ```

2. **Error Rate**
   ```promql
   rate(http_errors_total[5m]) / rate(http_requests_total[5m])
   ```

3. **P95 Latency**
   ```promql
   histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
   ```

4. **Active Requests**
   ```promql
   http_requests_in_progress
   ```

## SLOs (Service Level Objectives)

Conforme Plano de Implementação (seção 2.5):

| Rota | SLO (p95) | SLO (error rate) | Alerta (threshold) |
|------|-----------|------------------|--------------------|
| GET /indicadores | ≤ 500 ms | ≤ 0.5% | p95 > 800 ms por 5 min |
| GET /mapa (≤10k feições) | ≤ 4000 ms | ≤ 1% | p95 > 6000 ms por 5 min |
| POST /etl/epi/upload | ≤ 2000 ms | ≤ 1% | p95 > 3000 ms por 5 min |
| POST /atividades/{id}/evidencias | ≤ 1500 ms | ≤ 2% | p95 > 2500 ms por 5 min |
| GET /relatorios/epi01 | ≤ 8000 ms | ≤ 1% | p95 > 12000 ms por 5 min |
| GET /exports/atividades.geojson | ≤ 3000 ms | ≤ 1% | p95 > 5000 ms por 5 min |

**Regras de Alerta (Prometheus):**

```yaml
groups:
  - name: techdengue_slos
    interval: 30s
    rules:
      # Latência P95 alta
      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Alta latência em {{ $labels.endpoint }}"
          description: "P95 latência é {{ $value }}s (threshold: 800ms)"

      # Taxa de erro alta
      - alert: HighErrorRate
        expr: rate(http_errors_total[5m]) / rate(http_requests_total[5m]) > 0.02
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Alta taxa de erro em {{ $labels.endpoint }}"
          description: "Error rate é {{ $value | humanizePercentage }} (threshold: 2%)"

      # API indisponível
      - alert: APIDown
        expr: up{job=~".*-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API {{ $labels.job }} indisponível"
          description: "A API não está respondendo ao healthcheck"
```

## Integração com OpenTelemetry

As APIs já incluem `opentelemetry-instrumentation-fastapi` para tracing distribuído.

**Configuração futura (quando coletor disponível):**

```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Configure tracer
trace.set_tracer_provider(TracerProvider())
otlp_exporter = OTLPSpanExporter(endpoint="otel-collector:4317")
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

# Instrument FastAPI
FastAPIInstrumentor.instrument_app(app)
```

## Logs - Aggregação e Query

### Loki (recomendado para logs)

**docker-compose.yml:**
```yaml
loki:
  image: grafana/loki:latest
  ports:
    - "3100:3100"
  command: -config.file=/etc/loki/local-config.yaml
```

**Promtail config (log shipper):**
```yaml
server:
  http_listen_port: 9080

positions:
  filename: /tmp/positions.yaml

clients:
  - url: http://loki:3100/loki/api/v1/push

scrape_configs:
  - job_name: techdengue-apis
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
    relabel_configs:
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'
```

**Query logs (LogQL):**
```logql
# Erros nas últimas 1h
{service="epi-api"} | json | level="ERROR" | line_format "{{.message}}"

# Latência > 500ms
{service="epi-api"} | json | latency_ms > 500

# Por request_id
{service="epi-api"} | json | request_id="f47ac10b-58cc-4372-a567-0e02b2c3d479"

# Taxa de erro por minuto
rate({service="epi-api"} | json | status_code >= 400 [1m])
```

## Debugging e Troubleshooting

### Trace de Request Completo

1. **Cliente envia request com X-Request-ID**
```bash
curl -H "X-Request-ID: debug-123" http://localhost:8000/api/health
```

2. **API loga com request_id**
```json
{
  "request_id": "debug-123",
  "method": "GET",
  "path": "/api/health",
  "status_code": 200,
  "latency_ms": 12.34
}
```

3. **Buscar todos os logs deste request**
```logql
{service=~".*-api"} | json | request_id="debug-123"
```

### Análise de Performance

**Top 10 endpoints mais lentos:**
```promql
topk(10, histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[1h])))
```

**Endpoints com mais erros:**
```promql
topk(10, rate(http_errors_total[1h]))
```

## Próximos Passos (M1+)

- [ ] Deploy Prometheus + Grafana no docker-compose
- [ ] Criar dashboards Grafana pré-configurados
- [ ] Configurar Loki + Promtail para agregação de logs
- [ ] Implementar alerting (AlertManager)
- [ ] Adicionar custom metrics de negócio (ETL, filas, etc.)
- [ ] Instrumentar queries SQL (latência por query)
- [ ] Adicionar tracing distribuído end-to-end
- [ ] Dashboard NOC (Network Operations Center) completo

## Referências

- Plano de Implementação: `docs/PLANO_DE_IMPLEMENTACAO.md` (seção 2.5)
- Prometheus: https://prometheus.io/
- OpenTelemetry: https://opentelemetry.io/
- Grafana Loki: https://grafana.com/oss/loki/
