# PWA Campo — Offline-First (IndexedDB + Fila de Sync)

Este pacote entrega:
- **IndexedDB** com stores: `atividades`, `evidencias`, `insumos`, `eventos` (fila).
- **Fila de Sync** idempotente com *backoff* e *last-write-wins*.
- **Service Worker (sw.js)** com cache do *app shell* e suporte a Background Sync (quando disponível).
- **Manifest** PWA.
- **Hooks** (React/TS) de uso rápido.

> Ajuste as URLs da API (`API_BASE`) e as rotas conforme sua infra.

## Instalação (no seu frontend/Windsurf)

1. Copie a pasta `pwa_offline/` para o repo, por exemplo para `frontend/`.
2. Instale dependências opcionais se desejar (mas o pacote usa **vanilla IndexedDB**, sem libs externas).
3. Registre o **service worker** no `index.tsx`/`main.tsx`:

```ts
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js');
  });
}
```

4. Garanta que `manifest.webmanifest` esteja servido em `/manifest.webmanifest` e inclua no `<head>`:
```html
<link rel="manifest" href="/manifest.webmanifest">
<meta name="theme-color" content="#00A8E8">
```

5. Importe e use os hooks e a fila:
```ts
import { dbReady, putAtividade, listAtividades } from './pwa_offline/src/indexeddb';
import { enqueueEvent, startSyncLoop } from './pwa_offline/src/syncQueue';

await dbReady;
await putAtividade({...});
const list = await listAtividades();

// Enfileirar evento de API (ex.: PATCH atividade)
await enqueueEvent({
  id: crypto.randomUUID(),
  type: 'PATCH_ATIVIDADE',
  url: '/v1/atividades/{id}',
  method: 'PATCH',
  body: { status: 'ENCERRADA' },
  idempotencyKey: crypto.randomUUID(),
  updatedAt: new Date().toISOString()
});

// Iniciar laço de sincronização (fallback ao Background Sync nativo)
startSyncLoop();
```

## Estratégia de sincronização

- Cada alteração local gera um **evento** no store `eventos` (fila).
- O **Service Worker** tenta enviar no gatilho do **Background Sync** (`sync`).
- Fallback (quando não há Background Sync): `startSyncLoop()` executa a cada 30s com *backoff*.
- **Idempotência**: cada evento carrega `idempotencyKey` e o servidor deve aceitar `Idempotency-Key` (header).
- **Conflitos**: política *last-write-wins* usando `updatedAt` (servidor decide).

## Estrutura de dados (stores)

- `atividades`: `{ id, origem, municipio_cod_ibge, bairro, equipe, sla_deadline, status, criado_em, atualizado_em }`
- `evidencias`: `{ id, atividade_id, uri, hash_sha256, lat, lon, tipo, capturado_em, criado_em }`
- `insumos`: `{ id, atividade_id, nome, lote, qtd, unidade, validade, criado_em }`
- `eventos`: `{ id, type, url, method, headers?, body?, idempotencyKey, updatedAt, attempts, lastError }`

## Observações

- `sw.js` contém uma **cache strategy** simples para o *app shell* e `fetch` dinâmico.
- Para uploads grandes de mídia, prefira **Presigned URLs** e suba direto ao S3 quando online; offline → enfileire metadados e suba após reconexão.
- Ajuste os caminhos de import conforme sua estrutura.
