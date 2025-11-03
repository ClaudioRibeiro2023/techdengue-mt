import type { DenunciaCreate } from '@/types/denuncia'

type QueueItem = { id?: number; payload: DenunciaCreate; createdAt: number }

const DB_NAME = 'eDenunciaDB'
const DB_VERSION = 1
const STORE = 'denunciasQueue'

function openDB(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE)) {
        db.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true })
      }
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

export async function enqueueDenuncia(payload: DenunciaCreate) {
  const db = await openDB()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    const store = tx.objectStore(STORE)
    store.add({ payload, createdAt: Date.now() })
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
  db.close()
}

async function getAllQueued(): Promise<QueueItem[]> {
  const db = await openDB()
  const items = await new Promise<QueueItem[]>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly')
    const store = tx.objectStore(STORE)
    const req = store.getAll()
    req.onsuccess = () => resolve(req.result || [])
    req.onerror = () => reject(req.error)
  })
  db.close()
  return items
}

async function removeById(id: number) {
  const db = await openDB()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    const store = tx.objectStore(STORE)
    store.delete(id)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error)
  })
  db.close()
}

export async function syncQueue() {
  if (!navigator.onLine) return { synced: 0, failed: 0 }
  const items = await getAllQueued()
  let synced = 0
  let failed = 0
  for (const item of items) {
    try {
      const res = await fetch('/api/denuncias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Offline-Sync': '1' },
        body: JSON.stringify(item.payload),
      })
      if (res.ok) {
        if (typeof item.id === 'number') {
          await removeById(item.id)
        }
        synced++
      } else {
        failed++
      }
    } catch {
      failed++
    }
  }
  return { synced, failed }
}
