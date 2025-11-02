/* Service Worker — PWA Campo (cache + background sync) */

const CACHE_NAME = 'td-app-shell-v1';
const APP_SHELL = [
  '/',
  '/index.html',
  '/manifest.webmanifest',
  // adicione seus bundles (ex.: '/assets/main.js', '/assets/styles.css')
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

// Cache-first para o app shell; network-first para API
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.pathname.startsWith('/v1/')) {
    // API — network first
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  } else {
    // App shell — cache first
    event.respondWith(
      caches.match(event.request).then((resp) => resp || fetch(event.request))
    );
  }
});

// Background Sync (quando disponível)
self.addEventListener('sync', async (event) => {
  if (event.tag === 'sync-events') {
    event.waitUntil(processQueue());
  }
});

// Comunicação com a página para acionar processQueue()
self.addEventListener('message', async (event) => {
  if (event.data && event.data.type === 'PROCESS_QUEUE') {
    await processQueue();
  }
});

// Minimal DB acessível no SW via IndexedDB
function openDb() {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open('techdengue-db', 1);
    req.onupgradeneeded = () => {
      const db = req.result;
      if (!db.objectStoreNames.contains('eventos')) {
        const store = db.createObjectStore('eventos', { keyPath: 'id' });
        store.createIndex('by_attempts', 'attempts');
      }
    };
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

async function getAllEvents(db) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('eventos', 'readonly');
    const store = tx.objectStore('eventos');
    const req = store.getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

async function deleteEvent(db, id) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('eventos', 'readwrite');
    const store = tx.objectStore('eventos');
    const req = store.delete(id);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

async function putEvent(db, evt) {
  return new Promise((resolve, reject) => {
    const tx = db.transaction('eventos', 'readwrite');
    const store = tx.objectStore('eventos');
    const req = store.put(evt);
    req.onsuccess = () => resolve();
    req.onerror = () => reject(req.error);
  });
}

async function processQueue() {
  const db = await openDb();
  const events = await getAllEvents(db);
  for (const evt of events) {
    try {
      const headers = Object.assign({
        'Content-Type': 'application/json',
        'Idempotency-Key': evt.idempotencyKey || evt.id
      }, evt.headers || {});

      const resp = await fetch(evt.url, {
        method: evt.method || 'POST',
        headers,
        body: evt.body ? JSON.stringify(evt.body) : undefined
      });

      if (resp.ok || resp.status === 409 /* idempotência */) {
        await deleteEvent(db, evt.id);
      } else {
        // incrementa tentativas
        evt.attempts = (evt.attempts || 0) + 1;
        evt.lastError = `HTTP ${resp.status}`;
        await putEvent(db, evt);
      }
    } catch (e) {
      evt.attempts = (evt.attempts || 0) + 1;
      evt.lastError = String(e);
      await putEvent(db, evt);
    }
  }
}
