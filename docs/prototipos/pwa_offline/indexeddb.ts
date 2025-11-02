// indexeddb.ts — IndexedDB minimalista (vanilla) para PWA Campo
import type { Atividade, Evidencia, InsumoMov, EventoFila } from './types';

const DB_NAME = 'techdengue-db';
const DB_VERSION = 1;

let dbPromise: Promise<IDBDatabase> | null = null;

export const dbReady = new Promise<void>((resolve, reject) => {
  openDb().then(() => resolve()).catch(reject);
});

export function openDb(): Promise<IDBDatabase> {
  if (dbPromise) return dbPromise;
  dbPromise = new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('atividades')) {
        const store = db.createObjectStore('atividades', { keyPath: 'id' });
        store.createIndex('by_status', 'status');
        store.createIndex('by_mun', 'municipio_cod_ibge');
      }
      if (!db.objectStoreNames.contains('evidencias')) {
        const store = db.createObjectStore('evidencias', { keyPath: 'id' });
        store.createIndex('by_atividade', 'atividade_id');
      }
      if (!db.objectStoreNames.contains('insumos')) {
        const store = db.createObjectStore('insumos', { keyPath: 'id' });
        store.createIndex('by_atividade', 'atividade_id');
      }
      if (!db.objectStoreNames.contains('eventos')) {
        const store = db.createObjectStore('eventos', { keyPath: 'id' });
        store.createIndex('by_attempts', 'attempts');
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
  return dbPromise;
}

// Helpers genéricos
function txStore<T=any>(storeName: string, mode: IDBTransactionMode, fn: (store: IDBObjectStore)=>Promise<T>) {
  return openDb().then(db => new Promise<T>((resolve, reject) => {
    const tx = db.transaction(storeName, mode);
    const store = tx.objectStore(storeName);
    fn(store).then(res => {
      tx.oncomplete = () => resolve(res);
      tx.onerror = () => reject(tx.error);
    }).catch(reject);
  }));
}

// Atividades
export function putAtividade(a: Atividade) {
  a.atualizado_em = a.atualizado_em || new Date().toISOString();
  return txStore('atividades', 'readwrite', (s) => new Promise((resolve, reject) => {
    const req = s.put(a);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  }));
}

export function getAtividade(id: string): Promise<Atividade | undefined> {
  return txStore('atividades', 'readonly', (s) => new Promise((resolve, reject) => {
    const req = s.get(id);
    req.onsuccess = () => resolve(req.result as Atividade | undefined);
    req.onerror = () => reject(req.error);
  }));
}

export function listAtividades(): Promise<Atividade[]> {
  return txStore('atividades', 'readonly', (s) => new Promise((resolve, reject) => {
    const req = s.getAll();
    req.onsuccess = () => resolve((req.result || []) as Atividade[]);
    req.onerror = () => reject(req.error);
  }));
}

// Evidências
export function putEvidencia(e: Evidencia) {
  return txStore('evidencias', 'readwrite', (s) => new Promise((resolve, reject) => {
    const req = s.put(e);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  }));
}

export function listEvidenciasByAtividade(atividade_id: string): Promise<Evidencia[]> {
  return openDb().then(db => new Promise((resolve, reject) => {
    const tx = db.transaction('evidencias', 'readonly');
    const store = tx.objectStore('evidencias');
    const idx = store.index('by_atividade');
    const req = idx.getAll(atividade_id);
    req.onsuccess = () => resolve((req.result || []) as Evidencia[]);
    req.onerror = () => reject(req.error);
  }));
}

// Insumos
export function putInsumo(i: InsumoMov) {
  return txStore('insumos', 'readwrite', (s) => new Promise((resolve, reject) => {
    const req = s.put(i);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  }));
}

export function listInsumosByAtividade(atividade_id: string): Promise<InsumoMov[]> {
  return openDb().then(db => new Promise((resolve, reject) => {
    const tx = db.transaction('insumos', 'readonly');
    const store = tx.objectStore('insumos');
    const idx = store.index('by_atividade');
    const req = idx.getAll(atividade_id);
    req.onsuccess = () => resolve((req.result || []) as InsumoMov[]);
    req.onerror = () => reject(req.error);
  }));
}

// Eventos (fila)
export function enqueueEvent(evt: EventoFila) {
  evt.attempts = evt.attempts || 0;
  return txStore('eventos', 'readwrite', (s) => new Promise((resolve, reject) => {
    const req = s.put(evt);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  }));
}

export async function getAllEvents(): Promise<EventoFila[]> {
  return txStore('eventos', 'readonly', (s) => new Promise((resolve, reject) => {
    const req = s.getAll();
    req.onsuccess = () => resolve((req.result || []) as EventoFila[]);
    req.onerror = () => reject(req.error);
  }));
}

export async function removeEvent(id: string) {
  return txStore('eventos', 'readwrite', (s) => new Promise((resolve, reject) => {
    const req = s.delete(id);
    req.onsuccess = () => resolve(true);
    req.onerror = () => reject(req.error);
  }));
}
