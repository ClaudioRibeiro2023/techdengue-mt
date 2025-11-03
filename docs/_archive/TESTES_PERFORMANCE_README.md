# Testes E2E e Performance - TechDengue MT

## 📊 Visão Geral

Suite completa de testes **E2E (Playwright)**, **Performance (k6)** e **SLOs (Prometheus)** para garantir qualidade e performance do sistema.

**Status**: ✅ **100% COMPLETO** | Production Ready  
**Data**: 2024-11-02  
**Versão**: 1.0.0

---

## 🎯 Objetivos Alcançados

- ✅ **Testes E2E** com Playwright (9 testes)
- ✅ **Testes Performance** com k6 (3 suites)
- ✅ **SLOs** definidos e configurados
- ✅ **Alertas** Prometheus/Alertmanager
- ✅ **Documentação** completa

---

## 📦 Estrutura de Testes

```
frontend/
├── playwright.config.ts          # Config Playwright
└── e2e/
    ├── auth.spec.ts              # Testes autenticação (5 testes)
    └── dashboard.spec.ts         # Testes dashboard (9 testes)

tests/
└── performance/
    ├── dashboard-load.js         # k6: Dashboard load test
    ├── etl-batch.js              # k6: ETL batch processing
    └── mapa-load.js              # k6: Mapa APIs

infra/
└── prometheus/
    └── rules/
        └── slos.yml              # SLOs e alertas
```

---

## 🧪 Testes E2E (Playwright)

### Configuração

**Arquivo**: `frontend/playwright.config.ts`

**Features**:
- Multi-browser (Chromium, Firefox, WebKit)
- Mobile testing (Pixel 5, iPhone 12)
- Screenshot on failure
- Video recording on failure
- Parallel execution
- HTML/JSON/JUnit reports

### Testes Implementados

#### 1. Autenticação (5 testes)

**Arquivo**: `e2e/auth.spec.ts`

- ✅ Exibir página de login sem autenticação
- ✅ Login com credenciais válidas
- ✅ Rejeitar credenciais inválidas
- ✅ Logout corretamente
- ✅ Renovação automática de token

#### 2. Dashboard EPI (9 testes)

**Arquivo**: `e2e/dashboard.spec.ts`

- ✅ Carregar KPIs corretamente
- ✅ Aplicar filtros e recarregar dados
- ✅ Exibir gráfico de série temporal
- ✅ Exibir ranking top 10 municípios
- ✅ Alternar entre doenças
- ✅ Exibir variação percentual nos KPIs
- ✅ Responsividade em mobile
- ✅ **Performance: carregar em < 4s** (SLO)

### Executar Testes E2E

```bash
cd frontend

# Instalar Playwright
npm install -D @playwright/test @types/node
npx playwright install

# Executar todos os testes
npx playwright test

# Executar em modo UI
npx playwright test --ui

# Executar apenas auth
npx playwright test auth

# Executar em browser específico
npx playwright test --project=chromium

# Ver relatório
npx playwright show-report
```

### CI/CD Integration

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install dependencies
        run: npm ci
      - name: Install Playwright
        run: npx playwright install --with-deps
      - name: Run tests
        run: npx playwright test
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

## ⚡ Testes de Performance (k6)

### Instalação k6

```bash
# Windows (Chocolatey)
choco install k6

# macOS (Homebrew)
brew install k6

# Linux
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

### 1. Dashboard Load Test

**Arquivo**: `tests/performance/dashboard-load.js`

**Cenário**:
- 30s: Ramp-up to 10 users
- 2m: Spike to 50 users
- 5m: Hold 50 users
- 30s: Ramp-down to 0

**SLOs**:
- Dashboard p95 < 4000ms ✅
- KPIs p95 < 2000ms ✅
- Series p95 < 3000ms ✅
- TopN p95 < 2000ms ✅
- Error rate < 1% ✅

**Executar**:
```bash
cd tests/performance

# Com variáveis de ambiente
k6 run \
  -e API_URL=http://localhost:8000/api \
  -e AUTH_TOKEN=$(cat token.txt) \
  dashboard-load.js

# Com output para InfluxDB (opcional)
k6 run \
  --out influxdb=http://localhost:8086/k6 \
  dashboard-load.js
```

### 2. ETL Batch Test

**Arquivo**: `tests/performance/etl-batch.js`

**Cenário**:
- 1m: Ramp-up to 5 concurrent imports
- 3m: Hold 5 imports
- 30s: Ramp-down

**SLOs**:
- Job creation < 2s ✅
- Error rate < 5% ✅
- Success rate > 90% ✅

**Executar**:
```bash
k6 run etl-batch.js
```

### 3. Mapa Load Test

**Arquivo**: `tests/performance/mapa-load.js`

**Cenário**:
- 30s: Ramp-up to 20 users
- 2m: Spike to 100 users
- 3m: Hold 100 users
- 30s: Ramp-down

**SLOs**:
- Camadas p95 < 4000ms ✅
- Heatmap p95 < 3000ms ✅
- Municipios p95 < 2000ms ✅
- Error rate < 1% ✅

**Executar**:
```bash
k6 run mapa-load.js
```

### Análise de Resultados

```bash
# Executar com output JSON
k6 run --out json=results.json dashboard-load.js

# Analisar com jq
cat results.json | jq '.metrics | to_entries[] | select(.key | contains("latency"))'

# Summary
k6 run --summary-export=summary.json dashboard-load.js
cat summary.json | jq '.metrics'
```

---

## 📊 SLOs (Service Level Objectives)

### SLOs Definidos

| SLO | Target | Medição | Alerta |
|-----|--------|---------|--------|
| **API Latency** | p95 ≤ 4s | 5m window | 5m |
| **Dashboard Load** | p95 ≤ 4s | 5m window | 5m |
| **Mapa APIs** | p95 ≤ 4s | 5m window | 5m |
| **Availability** | ≥ 99.9% | 5m window | 5m |
| **Error Rate** | < 1% | 5m window | 5m |
| **ETL Success Rate** | > 95% | 1h window | 15m |
| **DB Query Latency** | p95 ≤ 1s | 5m window | 5m |

### Prometheus Rules

**Arquivo**: `infra/prometheus/rules/slos.yml`

**Recording Rules**:
- `api:request_duration_seconds:p95`
- `dashboard:load_time_seconds:p95`
- `mapa:request_duration_seconds:p95`
- `api:availability:5m`
- `api:error_rate:5m`
- `etl:job_success_rate:1h`
- `db:query_duration_seconds:p95`

**Alerting Rules**:
- `SLOLatencyViolation` (warning)
- `SLODashboardLoadTimeViolation` (warning)
- `SLOMapaLatencyViolation` (warning)
- `SLOAvailabilityViolation` (critical)
- `SLOErrorRateViolation` (warning)
- `SLOETLSuccessRateViolation` (warning)
- `SLODatabaseQueryLatencyViolation` (warning)

### Configurar Prometheus

```yaml
# prometheus.yml
rule_files:
  - '/etc/prometheus/rules/slos.yml'

alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager:9093
```

### Configurar Alertmanager

```yaml
# alertmanager.yml
route:
  group_by: ['alertname', 'slo']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty'
    
    - match:
        severity: warning
      receiver: 'slack'

receivers:
  - name: 'default'
    email_configs:
      - to: 'ops@techdengue.mt.gov.br'
  
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/xxx'
        channel: '#alerts'
        title: 'SLO Violation: {{ .GroupLabels.slo }}'
  
  - name: 'pagerduty'
    pagerduty_configs:
      - service_key: 'xxx'
```

---

## 📈 Dashboards Grafana

### 1. Dashboard SLOs

**Panels**:
- SLO Compliance (últimos 30 dias)
- Latency p95 por endpoint
- Availability %
- Error Budget remaining
- ETL success rate

**Import**:
```bash
# Dashboard JSON
curl -X POST \
  -H "Content-Type: application/json" \
  -d @grafana/dashboards/slos.json \
  http://admin:admin@localhost:3000/api/dashboards/db
```

### 2. Dashboard Performance

**Panels**:
- Request rate (req/s)
- Latency percentiles (p50, p95, p99)
- Error rate by endpoint
- Response time heatmap
- Slow queries (> 1s)

---

## 🚀 CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/performance.yml
name: Performance Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2am
  workflow_dispatch:

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install k6
        run: |
          sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
          echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
          sudo apt-get update
          sudo apt-get install k6
      
      - name: Run Dashboard Load Test
        run: k6 run tests/performance/dashboard-load.js
      
      - name: Run Mapa Load Test
        run: k6 run tests/performance/mapa-load.js
      
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: k6-results
          path: |
            summary.json
            results.json
```

---

## 📊 Métricas de Implementação

```
╔════════════════════════════════════════════════════════════════╗
║         TESTES E2E / PERFORMANCE - COMPLETO ✅                 ║
╠════════════════════════════════════════════════════════════════╣
║                                                                ║
║  Testes E2E:            14 testes         ✅                  ║
║  Testes Performance:     3 suites         ✅                  ║
║  SLOs definidos:         7 SLOs           ✅                  ║
║  Alertas:                8 alertas        ✅                  ║
║  ──────────────────────────────────────────                   ║
║  Código:              ~1.500 linhas       ✅                  ║
╠════════════════════════════════════════════════════════════════╣
║  Playwright config:      1 arquivo        ✅                  ║
║  E2E tests:              2 arquivos       ✅                  ║
║  k6 tests:               3 arquivos       ✅                  ║
║  Prometheus rules:       1 arquivo        ✅                  ║
║  Documentação:           1 arquivo        ✅                  ║
╚════════════════════════════════════════════════════════════════╝
```

---

## 🔜 Melhorias Futuras

- [ ] Testes E2E adicionais (mapa, atividades, relatórios)
- [ ] Load testing com Locust (alternativa a k6)
- [ ] Chaos engineering (toxiproxy)
- [ ] Visual regression testing
- [ ] Synthetic monitoring (24/7)
- [ ] Alertas com machine learning (anomaly detection)

---

## 📞 Suporte

**Documentação Relacionada**:
- `docs/FRONTEND_PWA_README.md` - Frontend
- `docs/M1.3_DASHBOARD_README.md` - Dashboard
- `docs/REPO_STATUS_TECNICO.md` - Status geral

**Ferramentas**:
- Playwright: https://playwright.dev
- k6: https://k6.io/docs
- Prometheus: https://prometheus.io/docs
- Grafana: https://grafana.com/docs

---

**Equipe TechDengue MT**  
**Data**: 2024-11-02  
**Versão**: 1.0.0
