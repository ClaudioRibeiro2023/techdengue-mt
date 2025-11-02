// syncQueue.ts — Fila de sincronização com backoff e idempotência
import { enqueueEvent, getAllEvents, removeEvent } from './indexeddb';
import type { EventoFila } from './types';

const API_BASE = '/v1';

let isProcessing = false;
let timer: number | null = null;
let intervalMs = 30000; // 30s base
const MAX_BACKOFF = 5 * 60 * 1000; // 5 min

export async function processQueueOnce() {
  if (isProcessing) return;
  isProcessing = true;
  try {
    const events = await getAllEvents();
    for (const evt of events) {
      await sendEvent(evt);
    }
  } finally {
    isProcessing = false;
  }
}

async function sendEvent(evt: EventoFila) {
  try {
    const url = evt.url.startsWith('http') ? evt.url : `${API_BASE}${evt.url}`;
    const headers: Record<string, string> = Object.assign({
      'Content-Type': 'application/json',
      'Idempotency-Key': evt.idempotencyKey || evt.id
    }, evt.headers || {});

    const resp = await fetch(url, {
      method: evt.method || 'POST',
      headers,
      body: evt.body ? JSON.stringify(evt.body) : undefined
    });

    if (resp.ok || resp.status === 409) {
      await removeEvent(evt.id);
      backoffReset();
      return;
    } else {
      throw new Error(`HTTP ${resp.status}`);
    }
  } catch (e: any) {
    // aumenta o backoff
    backoffIncrease();
    // mantém o evento; o SW/loop tentará novamente
    console.warn('sync error', evt.id, e?.message || e);
  }
}

function backoffIncrease() {
  intervalMs = Math.min(intervalMs * 2, MAX_BACKOFF);
}

function backoffReset() {
  intervalMs = 30000;
}

export function startSyncLoop() {
  if (timer) return;
  const tick = async () => {
    await processQueueOnce();
    timer = setTimeout(tick, intervalMs) as any as number;
  };
  // também solicita o SW (se existir) processar a fila
  if (navigator.serviceWorker && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage({ type: 'PROCESS_QUEUE' });
  }
  tick();
}

// Utilitário: disparar Background Sync quando disponível
export async function requestBackgroundSync() {
  if ('serviceWorker' in navigator && 'SyncManager' in window) {
    const reg = await navigator.serviceWorker.ready;
    try {
      await reg.sync.register('sync-events');
    } catch {
      // ignorar
    }
  }
}
