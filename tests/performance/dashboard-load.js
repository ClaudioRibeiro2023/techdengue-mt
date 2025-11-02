/**
 * k6 Performance Test - Dashboard EPI Load Test
 * 
 * Objetivo: Testar latência p95 das rotas de dashboard ≤ 4s
 * 
 * Executar: k6 run dashboard-load.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');
const dashboardLatency = new Trend('dashboard_latency');
const kpisLatency = new Trend('kpis_latency');
const seriesLatency = new Trend('series_latency');
const topNLatency = new Trend('topn_latency');

// Configuração do teste
export const options = {
  stages: [
    { duration: '30s', target: 10 },   // Ramp-up to 10 users
    { duration: '2m', target: 50 },    // Spike to 50 users
    { duration: '5m', target: 50 },    // Stay at 50 for 5 minutes
    { duration: '30s', target: 0 },    // Ramp-down to 0 users
  ],
  thresholds: {
    // SLO: p95 ≤ 4000ms
    'dashboard_latency': ['p(95)<4000'],
    'kpis_latency': ['p(95)<2000'],
    'series_latency': ['p(95)<3000'],
    'topn_latency': ['p(95)<2000'],
    // Taxa de erro < 1%
    'errors': ['rate<0.01'],
    // Requisições OK > 99%
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000/api';
const TOKEN = __ENV.AUTH_TOKEN || 'eyJhbGciOiJSUzI1NiIsInR5cCI...'; // Token válido

export default function () {
  const headers = {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  // 1. GET KPIs
  let response = http.get(`${BASE_URL}/indicadores/kpis?ano=2024`, { headers });
  
  check(response, {
    'KPIs status is 200': (r) => r.status === 200,
    'KPIs has data': (r) => r.json('total_casos') !== undefined,
  }) || errorRate.add(1);
  
  kpisLatency.add(response.timings.duration);
  
  sleep(1);

  // 2. GET Series Temporais
  response = http.get(`${BASE_URL}/indicadores/series-temporais?ano=2024&periodo_agregacao=semanal`, { headers });
  
  check(response, {
    'Series status is 200': (r) => r.status === 200,
    'Series has series array': (r) => Array.isArray(r.json('series')),
  }) || errorRate.add(1);
  
  seriesLatency.add(response.timings.duration);
  
  sleep(1);

  // 3. GET Top N
  response = http.get(`${BASE_URL}/indicadores/top?ano=2024&tipo_indicador=casos&limite=10`, { headers });
  
  check(response, {
    'TopN status is 200': (r) => r.status === 200,
    'TopN has ranking': (r) => Array.isArray(r.json('ranking')),
  }) || errorRate.add(1);
  
  topNLatency.add(response.timings.duration);
  
  sleep(1);

  // 4. Dashboard completo (todas as requisições em paralelo)
  const startTime = Date.now();
  
  const responses = http.batch([
    ['GET', `${BASE_URL}/indicadores/kpis?ano=2024`, null, { headers }],
    ['GET', `${BASE_URL}/indicadores/series-temporais?ano=2024&periodo_agregacao=semanal`, null, { headers }],
    ['GET', `${BASE_URL}/indicadores/top?ano=2024&tipo_indicador=casos&limite=10`, null, { headers }],
  ]);
  
  const totalTime = Date.now() - startTime;
  dashboardLatency.add(totalTime);
  
  check(responses, {
    'All dashboard requests successful': (r) => r.every(res => res.status === 200),
  }) || errorRate.add(1);
  
  sleep(2);
}

export function handleSummary(data) {
  return {
    'stdout': textSummary(data, { indent: ' ', enableColors: true }),
    'summary.json': JSON.stringify(data),
  };
}

function textSummary(data, options) {
  const { indent = '', enableColors = false } = options;
  
  let output = '\n';
  output += `${indent}Dashboard Performance Test Summary:\n`;
  output += `${indent}===================================\n\n`;
  
  // Métricas principais
  const metrics = data.metrics;
  
  output += `${indent}Dashboard Latency:\n`;
  output += `${indent}  p95: ${metrics.dashboard_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `${indent}  p99: ${metrics.dashboard_latency.values['p(99)'].toFixed(2)}ms\n`;
  output += `${indent}  avg: ${metrics.dashboard_latency.values.avg.toFixed(2)}ms\n\n`;
  
  output += `${indent}API Endpoints:\n`;
  output += `${indent}  KPIs p95: ${metrics.kpis_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `${indent}  Series p95: ${metrics.series_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `${indent}  TopN p95: ${metrics.topn_latency.values['p(95)'].toFixed(2)}ms\n\n`;
  
  output += `${indent}Error Rate: ${(metrics.errors.values.rate * 100).toFixed(2)}%\n`;
  output += `${indent}Requests: ${metrics.http_reqs.values.count}\n`;
  output += `${indent}Failed: ${metrics.http_req_failed.values.rate * 100}%\n`;
  
  return output;
}
