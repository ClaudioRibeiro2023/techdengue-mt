/**
 * k6 Performance Test - ETL Batch Processing
 * 
 * Objetivo: Testar processamento de lotes ETL e latência de jobs
 * 
 * Executar: k6 run etl-batch.js
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('errors');
const jobCreationLatency = new Trend('job_creation_latency');
const jobCompletionTime = new Trend('job_completion_time');
const jobsCreated = new Counter('jobs_created');
const jobsCompleted = new Counter('jobs_completed');

export const options = {
  stages: [
    { duration: '1m', target: 5 },    // 5 concurrent ETL imports
    { duration: '3m', target: 5 },    // Hold 5 for 3 minutes
    { duration: '30s', target: 0 },   // Ramp-down
  ],
  thresholds: {
    // Criação de job < 2s
    'job_creation_latency': ['p(95)<2000'],
    // Taxa de erro < 5% (ETL pode ter falhas)
    'errors': ['rate<0.05'],
  },
};

const BASE_URL = __ENV.API_URL || 'http://localhost:8000/api';
const TOKEN = __ENV.AUTH_TOKEN || 'token';

export default function () {
  const headers = {
    'Authorization': `Bearer ${TOKEN}`,
    'Content-Type': 'application/json',
  };

  // 1. Solicitar importação SINAN (simulado)
  const sinanPayload = JSON.stringify({
    arquivo_csv: '/data/sinan_2024_test.csv',
    ano: 2024,
    doenca_tipo: 'DENGUE',
  });

  let response = http.post(`${BASE_URL}/etl/sinan/import`, sinanPayload, { headers });
  
  check(response, {
    'SINAN import accepted': (r) => r.status === 202,
    'Job ID returned': (r) => r.json('job_id') !== undefined,
  }) || errorRate.add(1);
  
  jobCreationLatency.add(response.timings.duration);
  
  if (response.status === 202) {
    jobsCreated.add(1);
    const jobId = response.json('job_id');
    
    // 2. Polling do status do job
    const startTime = Date.now();
    let jobCompleted = false;
    let attempts = 0;
    const maxAttempts = 60; // 60 * 2s = 2 minutos max
    
    while (!jobCompleted && attempts < maxAttempts) {
      sleep(2);
      attempts++;
      
      response = http.get(`${BASE_URL}/etl/jobs/${jobId}`, { headers });
      
      if (response.status === 200) {
        const status = response.json('status');
        
        if (status === 'COMPLETED') {
          jobCompleted = true;
          jobsCompleted.add(1);
          const completionTime = Date.now() - startTime;
          jobCompletionTime.add(completionTime);
          
          console.log(`Job ${jobId} completed in ${completionTime}ms`);
          break;
        } else if (status === 'FAILED') {
          errorRate.add(1);
          console.error(`Job ${jobId} failed`);
          break;
        }
      }
    }
    
    if (!jobCompleted) {
      console.warn(`Job ${jobId} timeout after ${attempts * 2}s`);
    }
  }
  
  sleep(5);
}

export function handleSummary(data) {
  const metrics = data.metrics;
  
  let output = '\n';
  output += 'ETL Batch Performance Test Summary:\n';
  output += '===================================\n\n';
  
  output += 'Job Creation:\n';
  output += `  p95: ${metrics.job_creation_latency.values['p(95)'].toFixed(2)}ms\n`;
  output += `  avg: ${metrics.job_creation_latency.values.avg.toFixed(2)}ms\n\n`;
  
  output += 'Job Completion:\n';
  output += `  p95: ${metrics.job_completion_time.values['p(95)'].toFixed(2)}ms\n`;
  output += `  avg: ${metrics.job_completion_time.values.avg.toFixed(2)}ms\n\n`;
  
  output += 'Jobs:\n';
  output += `  Created: ${metrics.jobs_created.values.count}\n`;
  output += `  Completed: ${metrics.jobs_completed.values.count}\n`;
  output += `  Success Rate: ${(metrics.jobs_completed.values.count / metrics.jobs_created.values.count * 100).toFixed(2)}%\n\n`;
  
  output += `Error Rate: ${(metrics.errors.values.rate * 100).toFixed(2)}%\n`;
  
  return {
    'stdout': output,
    'summary.json': JSON.stringify(data),
  };
}
