/**
 * IndexedDB Service - Offline-first data storage
 */

const DB_NAME = 'techdengue-db';
const DB_VERSION = 1;

// Object stores
const STORES = {
  ATIVIDADES: 'atividades',
  EVIDENCIAS: 'evidencias',
  SYNC_QUEUE: 'syncQueue',
  CACHE_API: 'cacheAPI',
  OFFLINE_QUEUE: 'offlineQueue',
};

export interface SyncQueueItem {
  id: string;
  type: 'CREATE' | 'UPDATE' | 'DELETE';
  entity: string;
  data: unknown;
  timestamp: number;
  retries: number;
  lastError?: string;
}

export interface CacheEntry {
  key: string;
  data: unknown;
  timestamp: number;
  ttl: number; // seconds
}

class DBService {
  private db: IDBDatabase | null = null;

  /**
   * Inicializa banco IndexedDB
   */
  async init(): Promise<void> {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onerror = () => {
        console.error('IndexedDB error:', request.error);
        reject(request.error);
      };

      request.onsuccess = () => {
        this.db = request.result;
        console.log('IndexedDB initialized');
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = (event.target as IDBOpenDBRequest).result;

        // Store: Atividades
        if (!db.objectStoreNames.contains(STORES.ATIVIDADES)) {
          const ativStore = db.createObjectStore(STORES.ATIVIDADES, {
            keyPath: 'id',
          });
          ativStore.createIndex('data_atividade', 'data_atividade', {
            unique: false,
          });
          ativStore.createIndex('status', 'status', { unique: false });
        }

        // Store: Evidências
        if (!db.objectStoreNames.contains(STORES.EVIDENCIAS)) {
          const evidStore = db.createObjectStore(STORES.EVIDENCIAS, {
            keyPath: 'id',
          });
          evidStore.createIndex('atividade_id', 'atividade_id', {
            unique: false,
          });
          evidStore.createIndex('upload_status', 'upload_status', {
            unique: false,
          });
        }

        // Store: Sync Queue
        if (!db.objectStoreNames.contains(STORES.SYNC_QUEUE)) {
          const syncStore = db.createObjectStore(STORES.SYNC_QUEUE, {
            keyPath: 'id',
          });
          syncStore.createIndex('timestamp', 'timestamp', { unique: false });
          syncStore.createIndex('entity', 'entity', { unique: false });
        }

        // Store: Cache API
        if (!db.objectStoreNames.contains(STORES.CACHE_API)) {
          const cacheStore = db.createObjectStore(STORES.CACHE_API, {
            keyPath: 'key',
          });
          cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
        }

        // Store: Offline Queue
        if (!db.objectStoreNames.contains(STORES.OFFLINE_QUEUE)) {
          db.createObjectStore(STORES.OFFLINE_QUEUE, {
            keyPath: 'id',
            autoIncrement: true,
          });
        }

        console.log('IndexedDB schema created');
      };
    });
  }

  /**
   * Adiciona item ao store
   */
  async add<T>(storeName: string, item: T): Promise<void> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.add(item);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Atualiza item no store
   */
  async put<T>(storeName: string, item: T): Promise<void> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.put(item);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Obtém item por ID
   */
  async get<T>(storeName: string, id: string | number): Promise<T | null> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.get(id);

      request.onsuccess = () => resolve(request.result || null);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Obtém todos os itens do store
   */
  async getAll<T>(storeName: string): Promise<T[]> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readonly');
      const store = transaction.objectStore(storeName);
      const request = store.getAll();

      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Remove item por ID
   */
  async delete(storeName: string, id: string | number): Promise<void> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.delete(id);

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  /**
   * Limpa todos os itens do store
   */
  async clear(storeName: string): Promise<void> {
    if (!this.db) throw new Error('DB not initialized');

    return new Promise((resolve, reject) => {
      const transaction = this.db!.transaction([storeName], 'readwrite');
      const store = transaction.objectStore(storeName);
      const request = store.clear();

      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  }

  // ========================================================================
  // SYNC QUEUE
  // ========================================================================

  /**
   * Adiciona item à fila de sincronização
   */
  async addToSyncQueue(item: Omit<SyncQueueItem, 'id'>): Promise<void> {
    const queueItem: SyncQueueItem = {
      ...item,
      id: `${item.entity}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
    };

    await this.add(STORES.SYNC_QUEUE, queueItem);
    console.log('Added to sync queue:', queueItem.id);
  }

  /**
   * Obtém todos os itens da fila de sync
   */
  async getSyncQueue(): Promise<SyncQueueItem[]> {
    return this.getAll<SyncQueueItem>(STORES.SYNC_QUEUE);
  }

  /**
   * Remove item da fila de sync
   */
  async removFromSyncQueue(id: string): Promise<void> {
    await this.delete(STORES.SYNC_QUEUE, id);
    console.log('Removed from sync queue:', id);
  }

  /**
   * Atualiza item da fila (incrementa retries)
   */
  async updateSyncQueueItem(
    id: string,
    updates: Partial<SyncQueueItem>
  ): Promise<void> {
    const item = await this.get<SyncQueueItem>(STORES.SYNC_QUEUE, id);
    if (!item) throw new Error(`Sync queue item ${id} not found`);

    await this.put(STORES.SYNC_QUEUE, { ...item, ...updates });
  }

  // ========================================================================
  // CACHE API
  // ========================================================================

  /**
   * Salva resposta da API no cache
   */
  async cacheAPIResponse(
    key: string,
    data: unknown,
    ttl: number = 3600
  ): Promise<void> {
    const entry: CacheEntry = {
      key,
      data,
      timestamp: Date.now(),
      ttl,
    };

    await this.put(STORES.CACHE_API, entry);
  }

  /**
   * Obtém resposta da API do cache
   */
  async getCachedAPIResponse(key: string): Promise<unknown | null> {
    const entry = await this.get<CacheEntry>(STORES.CACHE_API, key);
    if (!entry) return null;

    // Verificar TTL
    const age = (Date.now() - entry.timestamp) / 1000;
    if (age > entry.ttl) {
      // Expirado
      await this.delete(STORES.CACHE_API, key);
      return null;
    }

    return entry.data;
  }

  /**
   * Limpa cache expirado
   */
  async cleanExpiredCache(): Promise<void> {
    const entries = await this.getAll<CacheEntry>(STORES.CACHE_API);
    const now = Date.now();

    for (const entry of entries) {
      const age = (now - entry.timestamp) / 1000;
      if (age > entry.ttl) {
        await this.delete(STORES.CACHE_API, entry.key);
      }
    }
  }

  // ========================================================================
  // ATIVIDADES
  // ========================================================================

  async saveAtividade(atividade: unknown): Promise<void> {
    await this.put(STORES.ATIVIDADES, atividade);
  }

  async getAtividades(): Promise<unknown[]> {
    return this.getAll(STORES.ATIVIDADES);
  }

  async deleteAtividade(id: string): Promise<void> {
    await this.delete(STORES.ATIVIDADES, id);
  }

  // ========================================================================
  // EVIDÊNCIAS
  // ========================================================================

  async saveEvidencia(evidencia: unknown): Promise<void> {
    await this.put(STORES.EVIDENCIAS, evidencia);
  }

  async getEvidencias(_atividadeId?: string): Promise<unknown[]> {
    // TODO: implementar filtro por index se _atividadeId fornecido
    return this.getAll(STORES.EVIDENCIAS);
  }

  async deleteEvidencia(id: string): Promise<void> {
    await this.delete(STORES.EVIDENCIAS, id);
  }
}

// Singleton
export const dbService = new DBService();

// Inicializar ao carregar
if (typeof window !== 'undefined') {
  dbService.init().catch((error) => {
    console.error('Failed to initialize IndexedDB:', error);
  });
}
