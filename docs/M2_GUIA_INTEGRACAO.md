# M2 Campo API - Guia de Integração

## 📱 Integração Frontend

### React/TypeScript - Exemplo Completo

#### 1. Configuração do Cliente API

```typescript
// src/api/campo-api.ts
import axios, { AxiosInstance } from 'axios';

export interface CampoAPIConfig {
  baseURL: string;
  timeout?: number;
}

export class CampoAPIClient {
  private client: AxiosInstance;

  constructor(config: CampoAPIConfig) {
    this.client = axios.create({
      baseURL: config.baseURL,
      timeout: config.timeout || 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Interceptor para adicionar token
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('access_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para refresh token
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Refresh token logic
          await this.refreshToken();
          return this.client.request(error.config);
        }
        return Promise.reject(error);
      }
    );
  }

  async refreshToken() {
    // Implementar lógica de refresh token
  }

  // Atividades
  async criarAtividade(data: AtividadeCreate): Promise<Atividade> {
    const response = await this.client.post('/atividades', data);
    return response.data;
  }

  async listarAtividades(params?: AtividadeListParams): Promise<AtividadeList> {
    const response = await this.client.get('/atividades', { params });
    return response.data;
  }

  async obterAtividade(id: number): Promise<Atividade> {
    const response = await this.client.get(`/atividades/${id}`);
    return response.data;
  }

  async atualizarAtividade(id: number, data: AtividadeUpdate): Promise<Atividade> {
    const response = await this.client.patch(`/atividades/${id}`, data);
    return response.data;
  }

  async deletarAtividade(id: number): Promise<void> {
    await this.client.delete(`/atividades/${id}`);
  }

  // Evidências
  async solicitarPresignedURL(
    atividadeId: number,
    data: PresignedURLRequest
  ): Promise<PresignedURLResponse> {
    const response = await this.client.post(
      `/atividades/${atividadeId}/evidencias/presigned-url`,
      data
    );
    return response.data;
  }

  async registrarEvidencia(
    atividadeId: number,
    data: EvidenciaCreate
  ): Promise<Evidencia> {
    const response = await this.client.post(
      `/atividades/${atividadeId}/evidencias`,
      data
    );
    return response.data;
  }

  async listarEvidencias(atividadeId: number): Promise<EvidenciaList> {
    const response = await this.client.get(`/atividades/${atividadeId}/evidencias`);
    return response.data;
  }

  // Relatórios
  async gerarRelatorioEVD01(params: EVD01Params): Promise<EVD01Response> {
    const response = await this.client.get('/relatorios/evd01', { params });
    return response.data;
  }
}

// Instância singleton
export const campoAPI = new CampoAPIClient({
  baseURL: process.env.REACT_APP_CAMPO_API_URL || 'http://localhost:8001/api'
});
```

#### 2. Hook React para Upload de Evidências

```typescript
// src/hooks/useEvidenciaUpload.ts
import { useState } from 'react';
import { campoAPI } from '../api/campo-api';

interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export function useEvidenciaUpload() {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);

  const upload = async (atividadeId: number, file: File) => {
    setUploading(true);
    setError(null);
    setProgress({ loaded: 0, total: file.size, percentage: 0 });

    try {
      // 1. Solicitar presigned URL
      const presignedData = await campoAPI.solicitarPresignedURL(atividadeId, {
        filename: file.name,
        content_type: file.type,
        tamanho_bytes: file.size
      });

      // 2. Upload direto ao S3
      await axios.put(presignedData.upload_url, file, {
        headers: {
          'Content-Type': file.type
        },
        onUploadProgress: (progressEvent) => {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || file.size)
          );
          setProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total || file.size,
            percentage
          });
        }
      });

      // 3. Calcular hash SHA-256
      const hash = await calculateSHA256(file);

      // 4. Registrar evidência no banco
      const evidencia = await campoAPI.registrarEvidencia(atividadeId, {
        atividade_id: atividadeId,
        tipo: getEvidenciaTipo(file.type),
        upload_id: presignedData.upload_id,
        hash_sha256: hash,
        tamanho_bytes: file.size,
        url_s3: presignedData.fields.key,
        descricao: file.name
      });

      setUploading(false);
      return evidencia;

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Erro no upload');
      setUploading(false);
      throw err;
    }
  };

  return { upload, uploading, progress, error };
}

// Calcular SHA-256 no browser
async function calculateSHA256(file: File): Promise<string> {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function getEvidenciaTipo(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'FOTO';
  if (mimeType.startsWith('video/')) return 'VIDEO';
  if (mimeType === 'application/pdf') return 'DOCUMENTO';
  if (mimeType.startsWith('audio/')) return 'AUDIO';
  return 'DOCUMENTO';
}
```

#### 3. Componente de Upload

```typescript
// src/components/EvidenciaUpload.tsx
import React, { useRef } from 'react';
import { useEvidenciaUpload } from '../hooks/useEvidenciaUpload';

interface Props {
  atividadeId: number;
  onUploadComplete: (evidencia: Evidencia) => void;
}

export function EvidenciaUpload({ atividadeId, onUploadComplete }: Props) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const { upload, uploading, progress, error } = useEvidenciaUpload();

  const handleFileSelect = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Validações
    if (file.size > 50 * 1024 * 1024) {
      alert('Arquivo muito grande! Máximo: 50MB');
      return;
    }

    try {
      const evidencia = await upload(atividadeId, file);
      onUploadComplete(evidencia);
      
      // Reset input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  return (
    <div className="evidencia-upload">
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*,video/*,application/pdf,audio/*"
        onChange={handleFileSelect}
        disabled={uploading}
      />

      {uploading && progress && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress.percentage}%` }}
            />
          </div>
          <span>{progress.percentage}% - {formatBytes(progress.loaded)} / {formatBytes(progress.total)}</span>
        </div>
      )}

      {error && (
        <div className="upload-error">
          Erro: {error}
        </div>
      )}
    </div>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
```

#### 4. Hook para Geolocalização

```typescript
// src/hooks/useGeolocation.ts
import { useState, useEffect } from 'react';

interface GeoPoint {
  type: 'Point';
  coordinates: [number, number, number?]; // [lon, lat, altitude?]
}

export function useGeolocation() {
  const [position, setPosition] = useState<GeoPoint | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const getCurrentPosition = () => {
    setLoading(true);
    setError(null);

    if (!navigator.geolocation) {
      setError('Geolocalização não suportada');
      setLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setPosition({
          type: 'Point',
          coordinates: [
            pos.coords.longitude,
            pos.coords.latitude,
            pos.coords.altitude || undefined
          ]
        });
        setLoading(false);
      },
      (err) => {
        setError(err.message);
        setLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
    );
  };

  return { position, error, loading, getCurrentPosition };
}
```

#### 5. Componente Completo de Atividade

```typescript
// src/components/AtividadeForm.tsx
import React, { useState } from 'react';
import { campoAPI } from '../api/campo-api';
import { useGeolocation } from '../hooks/useGeolocation';
import { EvidenciaUpload } from './EvidenciaUpload';

export function AtividadeForm() {
  const [tipo, setTipo] = useState('VISTORIA');
  const [descricao, setDescricao] = useState('');
  const [atividadeId, setAtividadeId] = useState<number | null>(null);
  const [evidencias, setEvidencias] = useState<Evidencia[]>([]);
  
  const { position, getCurrentPosition } = useGeolocation();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const atividade = await campoAPI.criarAtividade({
        tipo,
        municipio_cod_ibge: '5103403', // Cuiabá
        localizacao: position || undefined,
        descricao,
        metadata: {
          app_version: '1.0.0',
          device: navigator.userAgent
        }
      });

      setAtividadeId(atividade.id);
      
      // Iniciar atividade
      await campoAPI.atualizarAtividade(atividade.id, {
        status: 'EM_ANDAMENTO'
      });

      alert(`Atividade ${atividade.id} criada e iniciada!`);
    } catch (err) {
      alert('Erro ao criar atividade');
    }
  };

  const handleEvidenciaComplete = (evidencia: Evidencia) => {
    setEvidencias([...evidencias, evidencia]);
  };

  const handleFinalizar = async () => {
    if (!atividadeId) return;

    try {
      await campoAPI.atualizarAtividade(atividadeId, {
        status: 'CONCLUIDA'
      });

      // Gerar relatório
      const relatorio = await campoAPI.gerarRelatorioEVD01({
        atividade_id: atividadeId,
        tamanho_pagina: 'A4',
        orientacao: 'portrait'
      });

      alert(`Atividade finalizada! Relatório: ${relatorio.arquivo}`);
      
      // Reset form
      setAtividadeId(null);
      setEvidencias([]);
      setDescricao('');
    } catch (err) {
      alert('Erro ao finalizar atividade');
    }
  };

  return (
    <div className="atividade-form">
      <h2>Nova Atividade de Campo</h2>

      {!atividadeId ? (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Tipo:</label>
            <select value={tipo} onChange={e => setTipo(e.target.value)}>
              <option value="VISTORIA">Vistoria</option>
              <option value="LIRAA">LIRAa</option>
              <option value="NEBULIZACAO">Nebulização</option>
            </select>
          </div>

          <div>
            <label>Descrição:</label>
            <textarea 
              value={descricao}
              onChange={e => setDescricao(e.target.value)}
              rows={4}
            />
          </div>

          <div>
            <button type="button" onClick={getCurrentPosition}>
              📍 Obter Localização
            </button>
            {position && (
              <span>
                Lat: {position.coordinates[1].toFixed(6)}, 
                Lon: {position.coordinates[0].toFixed(6)}
              </span>
            )}
          </div>

          <button type="submit">Criar Atividade</button>
        </form>
      ) : (
        <div>
          <h3>Atividade #{atividadeId} - Em Andamento</h3>
          
          <div>
            <h4>Evidências ({evidencias.length})</h4>
            <EvidenciaUpload 
              atividadeId={atividadeId}
              onUploadComplete={handleEvidenciaComplete}
            />

            <ul>
              {evidencias.map(ev => (
                <li key={ev.id}>
                  {ev.tipo} - {ev.descricao} ({(ev.tamanho_bytes / 1024).toFixed(1)} KB)
                </li>
              ))}
            </ul>
          </div>

          <button onClick={handleFinalizar} disabled={evidencias.length === 0}>
            ✅ Finalizar Atividade
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 🔒 Segurança e Boas Práticas

### 1. Validação no Cliente

```typescript
// src/utils/validation.ts

export function validarMunicipio(codigo: string): boolean {
  // MT: 51xxxxx (7 dígitos)
  return /^51\d{5}$/.test(codigo);
}

export function validarCoordenadas(lon: number, lat: number): boolean {
  // Bounds Mato Grosso
  const LON_MIN = -61.6;
  const LON_MAX = -50.0;
  const LAT_MIN = -18.1;
  const LAT_MAX = -7.3;

  return lon >= LON_MIN && lon <= LON_MAX && 
         lat >= LAT_MIN && lat <= LAT_MAX;
}

export function validarTamanhoArquivo(bytes: number): boolean {
  return bytes <= 50 * 1024 * 1024; // 50MB
}

export function validarTipoArquivo(mimeType: string): boolean {
  const allowed = [
    'image/jpeg', 'image/png', 'image/webp',
    'video/mp4', 'video/quicktime',
    'application/pdf',
    'audio/mpeg', 'audio/wav'
  ];
  return allowed.includes(mimeType);
}
```

### 2. Retry Logic

```typescript
// src/utils/retry.ts

export async function retryOperation<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  delayMs: number = 1000
): Promise<T> {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      
      console.log(`Attempt ${attempt} failed, retrying in ${delayMs}ms...`);
      await new Promise(resolve => setTimeout(resolve, delayMs));
      delayMs *= 2; // Exponential backoff
    }
  }
  throw new Error('Max retries exceeded');
}

// Uso
const evidencia = await retryOperation(() => 
  campoAPI.registrarEvidencia(atividadeId, data)
);
```

### 3. Cache com IndexedDB

```typescript
// src/utils/cache.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';

interface CampoDBSchema extends DBSchema {
  atividades: {
    key: number;
    value: Atividade;
    indexes: { 'by-status': string };
  };
  evidencias: {
    key: number;
    value: Evidencia;
    indexes: { 'by-atividade': number };
  };
}

let db: IDBPDatabase<CampoDBSchema>;

export async function initDB() {
  db = await openDB<CampoDBSchema>('campo-db', 1, {
    upgrade(db) {
      const atividadeStore = db.createObjectStore('atividades', { keyPath: 'id' });
      atividadeStore.createIndex('by-status', 'status');

      const evidenciaStore = db.createObjectStore('evidencias', { keyPath: 'id' });
      evidenciaStore.createIndex('by-atividade', 'atividade_id');
    }
  });
}

export async function cacheAtividade(atividade: Atividade) {
  await db.put('atividades', atividade);
}

export async function getAtividade(id: number): Promise<Atividade | undefined> {
  return await db.get('atividades', id);
}

export async function listAtividadesPendentes(): Promise<Atividade[]> {
  return await db.getAllFromIndex('atividades', 'by-status', 'EM_ANDAMENTO');
}
```

---

## 📱 PWA - Service Worker

### 1. Configuração Básica

```typescript
// public/service-worker.js

const CACHE_NAME = 'campo-v1';
const urlsToCache = [
  '/',
  '/static/css/main.css',
  '/static/js/main.js',
  '/manifest.json'
];

// Install
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(urlsToCache))
  );
});

// Fetch
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request)
      .then((response) => {
        // Cache hit
        if (response) return response;

        // Network request
        return fetch(event.request).then((response) => {
          // Cache API responses
          if (event.request.url.includes('/api/')) {
            const responseClone = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(event.request, responseClone);
            });
          }
          return response;
        });
      })
      .catch(() => {
        // Offline fallback
        return caches.match('/offline.html');
      })
  );
});

// Background Sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-evidencias') {
    event.waitUntil(syncPendingUploads());
  }
});

async function syncPendingUploads() {
  // Get pending uploads from IndexedDB
  // Upload to API
  // Clear from IndexedDB on success
}
```

### 2. Manifest PWA

```json
// public/manifest.json
{
  "name": "TechDengue Campo",
  "short_name": "Campo",
  "description": "App de campo para vigilância epidemiológica",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#003366",
  "orientation": "portrait",
  "icons": [
    {
      "src": "/icons/icon-192x192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "/icons/icon-512x512.png",
      "sizes": "512x512",
      "type": "image/png"
    }
  ],
  "screenshots": [
    {
      "src": "/screenshots/home.png",
      "sizes": "540x720",
      "type": "image/png"
    }
  ],
  "shortcuts": [
    {
      "name": "Nova Atividade",
      "url": "/atividades/nova",
      "icons": [{ "src": "/icons/add-192.png", "sizes": "192x192" }]
    }
  ]
}
```

---

## 🧪 Testes

### 1. Testes Unitários (Jest)

```typescript
// src/__tests__/utils/validation.test.ts
import { validarMunicipio, validarCoordenadas } from '../utils/validation';

describe('Validation Utils', () => {
  describe('validarMunicipio', () => {
    it('deve aceitar código MT válido', () => {
      expect(validarMunicipio('5103403')).toBe(true); // Cuiabá
    });

    it('deve rejeitar código inválido', () => {
      expect(validarMunicipio('1234567')).toBe(false);
      expect(validarMunicipio('510340')).toBe(false); // 6 dígitos
    });
  });

  describe('validarCoordenadas', () => {
    it('deve aceitar coordenadas MT válidas', () => {
      expect(validarCoordenadas(-56.0967, -15.6014)).toBe(true);
    });

    it('deve rejeitar coordenadas fora de MT', () => {
      expect(validarCoordenadas(-45.0, -15.0)).toBe(false);
    });
  });
});
```

### 2. Testes de Integração (Cypress)

```typescript
// cypress/e2e/atividade-flow.cy.ts

describe('Fluxo Completo de Atividade', () => {
  it('deve criar atividade, fazer upload e gerar relatório', () => {
    cy.visit('/');
    
    // Login
    cy.get('[data-cy=login-btn]').click();
    cy.get('[data-cy=username]').type('agente_campo');
    cy.get('[data-cy=password]').type('senha123');
    cy.get('[data-cy=submit]').click();

    // Criar atividade
    cy.get('[data-cy=nova-atividade]').click();
    cy.get('[data-cy=tipo]').select('VISTORIA');
    cy.get('[data-cy=descricao]').type('Teste E2E');
    cy.get('[data-cy=criar]').click();

    // Upload foto
    cy.get('[data-cy=upload-input]').selectFile('cypress/fixtures/foto.jpg');
    cy.get('[data-cy=upload-progress]').should('be.visible');
    cy.get('[data-cy=evidencia-item]').should('have.length', 1);

    // Finalizar
    cy.get('[data-cy=finalizar]').click();
    cy.get('[data-cy=relatorio-link]').should('be.visible');
  });
});
```

---

## 📊 Monitoramento

### 1. Error Tracking (Sentry)

```typescript
// src/monitoring/sentry.ts
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN,
  environment: process.env.NODE_ENV,
  integrations: [
    new Sentry.BrowserTracing(),
    new Sentry.Replay()
  ],
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0
});

// Wrapper para funções async
export function withSentry<T>(fn: () => Promise<T>) {
  return Sentry.withScope(async () => {
    try {
      return await fn();
    } catch (error) {
      Sentry.captureException(error);
      throw error;
    }
  });
}
```

### 2. Analytics (Google Analytics)

```typescript
// src/monitoring/analytics.ts
export function trackEvent(
  category: string,
  action: string,
  label?: string,
  value?: number
) {
  if (window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value
    });
  }
}

// Uso
trackEvent('Atividade', 'create', 'VISTORIA');
trackEvent('Evidencia', 'upload', 'FOTO', fileSize);
trackEvent('Relatorio', 'generate', 'EVD01');
```

---

## 🚀 Deployment

### 1. Build Otimizado

```json
// package.json
{
  "scripts": {
    "build": "react-scripts build",
    "build:prod": "GENERATE_SOURCEMAP=false react-scripts build",
    "analyze": "source-map-explorer 'build/static/js/*.js'"
  },
  "dependencies": {
    "@sentry/react": "^7.0.0",
    "axios": "^1.6.0",
    "idb": "^7.1.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
```

### 2. Nginx Configuration

```nginx
# nginx.conf
server {
    listen 80;
    server_name campo.techdengue.mt.gov.br;

    root /usr/share/nginx/html;
    index index.html;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;

    # Cache assets
    location /static/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Service Worker (no cache)
    location = /service-worker.js {
        add_header Cache-Control "no-cache";
    }

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API Proxy
    location /api/ {
        proxy_pass http://campo-api:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📝 Checklist de Produção

- [ ] Implementar autenticação OAuth2/OIDC
- [ ] Configurar refresh token automático
- [ ] Adicionar validação offline com IndexedDB
- [ ] Implementar queue de sync para evidências
- [ ] Configurar Service Worker para cache
- [ ] Adicionar error tracking (Sentry)
- [ ] Configurar analytics (GA4)
- [ ] Implementar rate limiting no cliente
- [ ] Adicionar retry logic com backoff
- [ ] Testar modo offline completo
- [ ] Otimizar bundle size (<300KB)
- [ ] Configurar PWA manifest
- [ ] Adicionar screenshots para app stores
- [ ] Implementar Deep Links
- [ ] Testar em dispositivos reais (Android/iOS)

---

**Versão**: 1.0.0  
**Última Atualização**: 2024-01-15  
**Próxima Revisão**: M3 (Sincronização Avançada)
