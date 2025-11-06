/**
 * Background Sync Service
 */
import { dbService, SyncQueueItem } from './dbService';
import axios from 'axios';
import { getAuthHeader } from './authService';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

class SyncService {
  private isSyncing = false;
  private syncInterval: number | null = null;

  /**
   * Inicia sincronização automática
   */
  startAutoSync(intervalMs: number = 60000): void {
    if (this.syncInterval) return;

    this.syncInterval = window.setInterval(() => {
      if (navigator.onLine) {
        this.sync();
      }
    }, intervalMs);

    console.log('Auto-sync started');
  }

  /**
   * Para sincronização automática
   */
  stopAutoSync(): void {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
      this.syncInterval = null;
      console.log('Auto-sync stopped');
    }
  }

  /**
   * Sincroniza fila de pendências
   */
  async sync(): Promise<void> {
    if (this.isSyncing) {
      console.log('Sync already in progress');
      return;
    }

    if (!navigator.onLine) {
      console.log('Offline, skipping sync');
      return;
    }

    this.isSyncing = true;

    try {
      const queue = await dbService.getSyncQueue();
      console.log(`Syncing ${queue.length} items...`);

      for (const item of queue) {
        try {
          await this.syncItem(item);
          await dbService.removFromSyncQueue(item.id);
        } catch (error) {
          console.error(`Failed to sync item ${item.id}:`, error);
          
          // Incrementar retries
          await dbService.updateSyncQueueItem(item.id, {
            retries: item.retries + 1,
            lastError: error instanceof Error ? error.message : 'Unknown error',
          });

          // Remover após 5 tentativas
          if (item.retries >= 5) {
            console.warn(`Removing item ${item.id} after 5 retries`);
            await dbService.removFromSyncQueue(item.id);
          }
        }
      }

      console.log('Sync completed');
    } finally {
      this.isSyncing = false;
    }
  }

  /**
   * Sincroniza item individual
   */
  private async syncItem(item: SyncQueueItem): Promise<void> {
    const headers = await getAuthHeader();
    const url = this.buildURL(item.entity, item.type, item.data as { id?: string } | undefined);

    switch (item.type) {
      case 'CREATE':
        await axios.post(url, item.data, { headers });
        break;

      case 'UPDATE':
        await axios.put(url, item.data, { headers });
        break;

      case 'DELETE':
        await axios.delete(url, { headers });
        break;
    }

    console.log(`Synced ${item.type} ${item.entity} ${item.id}`);
  }

  /**
   * Constrói URL para sync
   */
  private buildURL(entity: string, type: 'CREATE' | 'UPDATE' | 'DELETE', data?: { id?: string }): string {
    switch (entity) {
      case 'atividade':
        return type === 'UPDATE' || type === 'DELETE'
          ? `${API_BASE_URL}/campo/atividades/${data?.id}`
          : `${API_BASE_URL}/campo/atividades`;

      case 'evidencia':
        return type === 'UPDATE' || type === 'DELETE'
          ? `${API_BASE_URL}/campo/evidencias/${data?.id}`
          : `${API_BASE_URL}/campo/evidencias`;

      default:
        throw new Error(`Unknown entity: ${entity}`);
    }
  }

  /**
   * Registra Service Worker para Background Sync
   */
  async registerBackgroundSync(): Promise<void> {
    if ('serviceWorker' in navigator && 'SyncManager' in window) {
      try {
        const registration = await navigator.serviceWorker.ready;
        type SyncCapable = ServiceWorkerRegistration & { sync?: { register: (name: string) => Promise<void> } }
        const reg = registration as SyncCapable
        if (reg.sync) {
          await reg.sync.register('sync-queue');
          console.log('Background sync registered');
        }
      } catch (error) {
        console.error('Background sync registration failed:', error);
      }
    }
  }
}

export const syncService = new SyncService();

// Iniciar auto-sync quando online
if (typeof window !== 'undefined') {
  window.addEventListener('online', () => {
    console.log('Online - triggering sync');
    syncService.sync();
  });

  // Iniciar auto-sync se já estiver online
  if (navigator.onLine) {
    syncService.startAutoSync();
  }
}
