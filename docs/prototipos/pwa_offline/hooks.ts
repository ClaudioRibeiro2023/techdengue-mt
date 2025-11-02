// hooks.ts — Hooks React auxiliares (opcional)
import { useEffect, useState } from 'react';
import { listAtividades, putAtividade } from './indexeddb';
import type { Atividade } from './types';
import { enqueueEvent, startSyncLoop, requestBackgroundSync } from './syncQueue';

export function useAtividades() {
  const [dados, setDados] = useState<Atividade[]>([]);
  useEffect(() => {
    let alive = true;
    (async () => {
      const list = await listAtividades();
      if (alive) setDados(list);
    })();
    return () => { alive = false; };
  }, []);
  return dados;
}

export async function criarOuAtualizarAtividadeLocal(a: Atividade) {
  await putAtividade(a);
  await enqueueEvent({
    id: crypto.randomUUID(),
    type: 'UPSERT_ATIVIDADE',
    url: `/atividades${a.id ? `/${a.id}`: ''}`,
    method: a.id ? 'PATCH' : 'POST',
    body: a,
    idempotencyKey: crypto.randomUUID(),
    updatedAt: new Date().toISOString()
  });
  await requestBackgroundSync();
  startSyncLoop();
}
