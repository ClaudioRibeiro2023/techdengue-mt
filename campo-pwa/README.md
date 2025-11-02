# TechDengue Campo PWA

Progressive Web App para coleta de dados em campo - Vigilância Epidemiológica do Mato Grosso.

## 🎯 Features

- ✅ Offline-first architecture
- ✅ IndexedDB para cache local
- ✅ Background sync para evidências
- ✅ Service Worker para cache
- ✅ Captura de foto/vídeo com watermark
- ✅ Geolocalização automática
- ✅ Upload direto para S3
- ✅ Geração de relatórios PDF

## 🏗️ Arquitetura

```
campo-pwa/
├── public/
│   ├── manifest.json          # PWA manifest
│   ├── service-worker.js      # Service Worker
│   └── icons/                 # App icons
├── src/
│   ├── api/                   # API clients
│   │   └── campo-api.ts
│   ├── components/            # React components
│   │   ├── Atividade/
│   │   ├── Evidencia/
│   │   └── Camera/
│   ├── hooks/                 # Custom hooks
│   │   ├── useGeolocation.ts
│   │   ├── useCamera.ts
│   │   └── useEvidenciaUpload.ts
│   ├── db/                    # IndexedDB
│   │   └── schema.ts
│   ├── utils/                 # Utilities
│   │   ├── watermark.ts
│   │   ├── hash.ts
│   │   └── validation.ts
│   └── workers/               # Web Workers
│       └── image-processor.worker.ts
└── package.json
```

## 🚀 Quick Start

```bash
# Instalar dependências
npm install

# Desenvolvimento
npm start

# Build produção
npm run build

# Testes
npm test

# E2E
npm run cypress:open
```

## 📦 Dependências Principais

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "idb": "^7.1.1",
    "date-fns": "^2.30.0",
    "@tanstack/react-query": "^5.0.0"
  },
  "devDependencies": {
    "@testing-library/react": "^14.0.0",
    "cypress": "^13.0.0",
    "typescript": "^5.0.0"
  }
}
```

## 🗄️ IndexedDB Schema

```typescript
// src/db/schema.ts
import { openDB, DBSchema, IDBPDatabase } from 'idb';

export interface CampoDBSchema extends DBSchema {
  atividades: {
    key: number;
    value: {
      id: number;
      tipo: string;
      status: string;
      municipio_cod_ibge: string;
      localizacao?: GeoJSON.Point;
      descricao?: string;
      metadata?: any;
      criado_em: string;
      atualizado_em: string;
      synced: boolean; // If synced to server
    };
    indexes: { 
      'by-status': string;
      'by-sync': boolean;
    };
  };
  evidencias: {
    key: number;
    value: {
      id: number;
      atividade_id: number;
      tipo: string;
      status: string;
      file_data?: Blob; // Temporary until uploaded
      hash_sha256: string;
      tamanho_bytes: number;
      url_s3?: string;
      url_download?: string;
      descricao?: string;
      metadata?: any;
      criado_em: string;
      synced: boolean;
    };
    indexes: { 
      'by-atividade': number;
      'by-sync': boolean;
    };
  };
  pending_uploads: {
    key: number;
    value: {
      id: number;
      atividade_id: number;
      file: Blob;
      filename: string;
      content_type: string;
      created_at: string;
      attempts: number;
    };
    indexes: { 'by-atividade': number };
  };
}

let db: IDBPDatabase<CampoDBSchema>;

export async function initDB() {
  db = await openDB<CampoDBSchema>('campo-db', 2, {
    upgrade(db, oldVersion, newVersion, transaction) {
      // Version 1
      if (oldVersion < 1) {
        const atividadeStore = db.createObjectStore('atividades', { keyPath: 'id' });
        atividadeStore.createIndex('by-status', 'status');
        atividadeStore.createIndex('by-sync', 'synced');

        const evidenciaStore = db.createObjectStore('evidencias', { keyPath: 'id' });
        evidenciaStore.createIndex('by-atividade', 'atividade_id');
        evidenciaStore.createIndex('by-sync', 'synced');
      }

      // Version 2
      if (oldVersion < 2) {
        const uploadStore = db.createObjectStore('pending_uploads', { 
          keyPath: 'id',
          autoIncrement: true
        });
        uploadStore.createIndex('by-atividade', 'atividade_id');
      }
    }
  });
  
  return db;
}

export function getDB() {
  if (!db) throw new Error('DB not initialized');
  return db;
}
```

## 📷 Camera Component

```typescript
// src/components/Camera/CameraCapture.tsx
import React, { useRef, useState, useEffect } from 'react';
import { applyWatermark } from '../../utils/watermark';
import { calculateSHA256 } from '../../utils/hash';

interface Props {
  onCapture: (file: File, metadata: CaptureMetadata) => void;
  watermarkText?: string;
}

interface CaptureMetadata {
  timestamp: Date;
  location?: GeolocationPosition;
  hash: string;
}

export function CameraCapture({ onCapture, watermarkText }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [capturing, setCapturing] = useState(false);

  useEffect(() => {
    startCamera();
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Back camera
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setStream(mediaStream);
    } catch (error) {
      console.error('Camera access denied:', error);
      alert('Erro ao acessar câmera. Verifique permissões.');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
    }
  };

  const capture = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    setCapturing(true);

    const video = videoRef.current;
    const canvas = canvasRef.current;
    
    // Set canvas size
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame
    const ctx = canvas.getContext('2d')!;
    ctx.drawImage(video, 0, 0);

    // Get geolocation
    let location: GeolocationPosition | undefined;
    try {
      location = await getCurrentPosition();
    } catch (err) {
      console.warn('Could not get location:', err);
    }

    // Apply watermark
    const timestamp = new Date();
    const watermark = watermarkText || 
      `${timestamp.toLocaleString('pt-BR')}\n` +
      `Lat: ${location?.coords.latitude.toFixed(6) || 'N/A'}\n` +
      `Lon: ${location?.coords.longitude.toFixed(6) || 'N/A'}`;
    
    applyWatermark(canvas, watermark);

    // Convert to blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      // Calculate hash
      const arrayBuffer = await blob.arrayBuffer();
      const hash = await calculateSHA256(arrayBuffer);

      // Create file
      const filename = `foto_${timestamp.getTime()}.jpg`;
      const file = new File([blob], filename, { type: 'image/jpeg' });

      // Callback
      onCapture(file, { timestamp, location, hash });
      
      setCapturing(false);
    }, 'image/jpeg', 0.9);
  };

  return (
    <div className="camera-capture">
      <video 
        ref={videoRef}
        autoPlay
        playsInline
        className="camera-preview"
      />
      <canvas ref={canvasRef} style={{ display: 'none' }} />
      
      <div className="camera-controls">
        <button 
          onClick={capture}
          disabled={capturing}
          className="capture-btn"
        >
          {capturing ? '⏳ Processando...' : '📷 Capturar'}
        </button>
      </div>
    </div>
  );
}

function getCurrentPosition(): Promise<GeolocationPosition> {
  return new Promise((resolve, reject) => {
    navigator.geolocation.getCurrentPosition(resolve, reject, {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    });
  });
}
```

## 🎨 Watermark Utility

```typescript
// src/utils/watermark.ts

export function applyWatermark(canvas: HTMLCanvasElement, text: string) {
  const ctx = canvas.getContext('2d')!;
  const lines = text.split('\n');
  
  // Semi-transparent background
  const padding = 15;
  const lineHeight = 25;
  const textHeight = lines.length * lineHeight + padding * 2;
  
  ctx.fillStyle = 'rgba(0, 0, 0, 0.6)';
  ctx.fillRect(10, canvas.height - textHeight - 10, canvas.width - 20, textHeight);
  
  // Text
  ctx.fillStyle = '#FFFFFF';
  ctx.font = 'bold 20px Arial';
  ctx.textAlign = 'left';
  
  lines.forEach((line, index) => {
    ctx.fillText(
      line,
      20,
      canvas.height - textHeight + padding + (index + 1) * lineHeight
    );
  });
}
```

## 🔐 SHA-256 Hash Utility

```typescript
// src/utils/hash.ts

export async function calculateSHA256(data: ArrayBuffer): Promise<string> {
  const hashBuffer = await crypto.subtle.digest('SHA-256', data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

export async function calculateSHA256FromFile(file: File): Promise<string> {
  const arrayBuffer = await file.arrayBuffer();
  return calculateSHA256(arrayBuffer);
}
```

## 🔄 Background Sync

```typescript
// public/service-worker.js

self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-evidencias') {
    event.waitUntil(syncPendingEvidencias());
  }
});

async function syncPendingEvidencias() {
  // Open IndexedDB
  const db = await openDB('campo-db', 2);
  
  // Get pending uploads
  const pending = await db.getAllFromIndex('pending_uploads', 'by-sync', false);
  
  for (const upload of pending) {
    try {
      // 1. Get presigned URL
      const presignedResponse = await fetch(
        `/api/atividades/${upload.atividade_id}/evidencias/presigned-url`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: upload.filename,
            content_type: upload.content_type,
            tamanho_bytes: upload.file.size
          })
        }
      );
      
      if (!presignedResponse.ok) {
        throw new Error('Failed to get presigned URL');
      }
      
      const presignedData = await presignedResponse.json();
      
      // 2. Upload to S3
      const uploadResponse = await fetch(presignedData.upload_url, {
        method: 'PUT',
        headers: { 'Content-Type': upload.content_type },
        body: upload.file
      });
      
      if (!uploadResponse.ok) {
        throw new Error('S3 upload failed');
      }
      
      // 3. Calculate hash
      const arrayBuffer = await upload.file.arrayBuffer();
      const hash = await calculateHash(arrayBuffer);
      
      // 4. Register evidence
      const evidenceResponse = await fetch(
        `/api/atividades/${upload.atividade_id}/evidencias`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            atividade_id: upload.atividade_id,
            tipo: getTipoFromMime(upload.content_type),
            upload_id: presignedData.upload_id,
            hash_sha256: hash,
            tamanho_bytes: upload.file.size,
            url_s3: presignedData.fields.key
          })
        }
      );
      
      if (evidenceResponse.ok) {
        // Remove from pending
        await db.delete('pending_uploads', upload.id);
      }
      
    } catch (error) {
      console.error('Sync failed for upload:', upload.id, error);
      
      // Increment attempts
      upload.attempts++;
      if (upload.attempts < 5) {
        await db.put('pending_uploads', upload);
      } else {
        // Max retries reached, notify user
        await showNotification('Upload falhou', {
          body: `Arquivo ${upload.filename} falhou após 5 tentativas`
        });
      }
    }
  }
}

async function calculateHash(arrayBuffer) {
  const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

function getTipoFromMime(mimeType) {
  if (mimeType.startsWith('image/')) return 'FOTO';
  if (mimeType.startsWith('video/')) return 'VIDEO';
  if (mimeType === 'application/pdf') return 'DOCUMENTO';
  if (mimeType.startsWith('audio/')) return 'AUDIO';
  return 'DOCUMENTO';
}
```

## 🧪 Testes

```typescript
// src/components/Camera/__tests__/CameraCapture.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CameraCapture } from '../CameraCapture';

// Mock getUserMedia
global.navigator.mediaDevices = {
  getUserMedia: jest.fn().mockResolvedValue({
    getTracks: () => [{ stop: jest.fn() }]
  })
};

describe('CameraCapture', () => {
  it('should request camera access on mount', async () => {
    render(<CameraCapture onCapture={jest.fn()} />);
    
    await waitFor(() => {
      expect(navigator.mediaDevices.getUserMedia).toHaveBeenCalledWith({
        video: expect.objectContaining({
          facingMode: 'environment'
        })
      });
    });
  });

  it('should capture photo on button click', async () => {
    const handleCapture = jest.fn();
    render(<CameraCapture onCapture={handleCapture} />);
    
    const captureBtn = screen.getByText(/capturar/i);
    await userEvent.click(captureBtn);
    
    await waitFor(() => {
      expect(handleCapture).toHaveBeenCalledWith(
        expect.any(File),
        expect.objectContaining({
          timestamp: expect.any(Date),
          hash: expect.any(String)
        })
      );
    });
  });
});
```

## 📱 PWA Install Prompt

```typescript
// src/hooks/usePWAInstall.ts
import { useState, useEffect } from 'react';

export function usePWAInstall() {
  const [installPrompt, setInstallPrompt] = useState<any>(null);
  const [isInstalled, setIsInstalled] = useState(false);

  useEffect(() => {
    // Check if already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsInstalled(true);
    }

    // Listen for install prompt
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setInstallPrompt(e);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const promptInstall = async () => {
    if (!installPrompt) return false;

    installPrompt.prompt();
    const { outcome } = await installPrompt.userChoice;
    
    if (outcome === 'accepted') {
      setIsInstalled(true);
      setInstallPrompt(null);
      return true;
    }
    
    return false;
  };

  return { installPrompt, isInstalled, promptInstall };
}
```

## 🚀 Deploy

### Build & Deploy

```bash
# Build
npm run build

# Deploy to Firebase Hosting
firebase deploy --only hosting

# Deploy to Netlify
netlify deploy --prod

# Deploy to Vercel
vercel --prod
```

### Environment Variables

```env
REACT_APP_CAMPO_API_URL=https://api.techdengue.mt.gov.br
REACT_APP_KEYCLOAK_URL=https://auth.techdengue.mt.gov.br
REACT_APP_KEYCLOAK_REALM=techdengue
REACT_APP_KEYCLOAK_CLIENT_ID=campo-pwa
REACT_APP_SENTRY_DSN=https://...
REACT_APP_GA_TRACKING_ID=G-...
```

---

## 📚 Recursos Adicionais

- [PWA Documentation](https://web.dev/progressive-web-apps/)
- [IndexedDB API](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Media Capture API](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)

---

**Versão**: 1.0.0  
**Licença**: MIT  
**Maintainer**: Equipe TechDengue
