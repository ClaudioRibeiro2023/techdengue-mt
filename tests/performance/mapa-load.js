/**
 * k6 Performance Test - Mapa APIs
 * 
 * Objetivo: Testar latência p95 das rotas de mapa ≤ 4s
 * 
 * Executar: k6 run mapa-load.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');
const camadasLatency = new Trend('camadas_latency');
const heatmapLatency = new Trend('heatmap_latency');
const municipiosLatency = new Trend('municipios_latency');

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp-up to 20 users
    { duration: '2m', target: 100 },   // Spike to 100 users
    { duration: '3m', target: 100 },   // Hold 100 for 3 minutes
    { duration: '30s', target: 0 },    // Ramp-down
  ],
  thresholds: {
    // SLO: p95 ≤ 4000ms
    'camadas_latency': ['p(95)<4000'],
    'heatmap_latency': ['p(95)<3000'],
    'municipios_latency': ['p(95)<2000'],
    // Taxa de erro < 1%
    'errors': ['rate<0.01'],
    'http_req_failed': ['rate<0.01'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000/api';
const TOKEN = __ENV.AUTH_TOKEN || 'token';

export default function () {
  const headers = {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  // 1. GET Camadas (choropleth)
  let response = http.get(
    `${BASE_URL}/mapa/camadas?ano=2024&tipo_camada=INCIDENCIA`,
    { headers }
  );
  
  check(response, {
    'Camadas status is 200': (r) => r.status === 200,
    'Camadas has features': (r) => {
      const data = r.json();
      return data.features && Array.isArray(data.features);
    },
  }) || errorRate.add(1);
  
  camadasLatency.add(response.timings.duration);
  
  sleep(0.5);

  // 2. GET Heatmap
  response = http.get(
    `${BASE_URL}/mapa/heatmap?ano=2024&semana_epi_inicio=1&semana_epi_fim=44`,
    { headers }
  );
  
  check(response, {
    'Heatmap status is 200': (r) => r.status === 200,
    'Heatmap has pontos': (r) => {
      const data = r.json();
      return data.pontos && Array.isArray(data.pontos);
    },
  }) || errorRate.add(1);
  
  heatmapLatency.add(response.timings.duration);
  
  sleep(0.5);

  // 3. GET Municípios
  response = http.get(`${BASE_URL}/mapa/municipios`, { headers });
  
  check(response, {
    'Municipios status is 200': (r) => r.status === 200,
    'Municipios is array': (r) => Array.isArray(r.json()),
  }) || errorRate.add(1);
  
  municipiosLatency.add(response.timings.duration);
  
  sleep(1);

  // 4. Requisições paralelas (carga de mapa completo)
  const responses = http.batch([
    ['GET', `${BASE_URL}/mapa/camadas?ano=2024&tipo_camada=INCIDENCIA`, null, { headers }],
    ['GET', `${BASE_URL}/mapa/heatmap?ano=2024`, null, { headers }],
    ['GET', `${BASE_URL}/mapa/municipios`, null, { headers }],
  ]);
  
  check(responses, {
    'All mapa requests successful': (r) => r.every(res => res.status === 200),
  }) || errorRate.add(1);
  
  sleep(2);
}

export function handleSummary(data) {
  const metrics = data.metrics;
  
  let output = '\n';
  output += 'Mapa Performance Test Summary:\n';
  output += '==============================\n\n';
  
  output += 'API Endpoints:\n';
  output += `  Camadas p95: ${metrics.camadas_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `  Camadas avg: ${metrics.camadas_latency.values.avg.toFixed(2)}ms\n`;
  output += `  Heatmap p95: ${metrics.heatmap_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `  Heatmap avg: ${metrics.heatmap_latency.values.avg.toFixed(2)}ms\n`;
  output += `  Municipios p95: ${metrics.municipios_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `  Municipios avg: ${metrics.municipios_latency.values.avg.toFixed(2)}ms\n\n`;
  
  output += `Error Rate: ${(metrics.errors.values.rate * 100).toFixed(2)}%\n`;
  output += `Requests: ${metrics.http_reqs.values.count}\n`;
  output += `RPS: ${metrics.http_reqs.values.rate.toFixed(2)}\n`;
  
  // Verificar SLO
  const camadasP95 = metrics.camadas_latency.values['p(95)'];
  const sloMet = camadasP95 <= 4000;
  output += `\nSLO (p95 ≤ 4s): ${sloMet ? '✅ MET' : '❌ VIOLATED'}\n`;
  
  return {
    'stdout': output,
    'summary.json': JSON.stringify(data),
  };
}
