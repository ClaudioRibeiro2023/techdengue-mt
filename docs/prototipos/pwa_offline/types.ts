// types.ts — Tipos base do PWA Campo

export type UUID = string;

export interface Atividade {
  id: UUID;
  origem: 'DENUNCIA' | 'PLANO' | 'ALERTA';
  municipio_cod_ibge: string;
  bairro?: string;
  equipe?: string;
  sla_deadline?: string; // ISO
  status: 'CRIADA' | 'EM_ANDAMENTO' | 'ENCERRADA';
  criado_em?: string;
  atualizado_em?: string;
}

export interface Evidencia {
  id: UUID;
  atividade_id: UUID;
  uri: string;
  hash_sha256: string;
  lat?: number;
  lon?: number;
  tipo: 'FOTO' | 'VIDEO';
  capturado_em: string;
  criado_em?: string;
}

export interface InsumoMov {
  id: UUID;
  atividade_id: UUID;
  nome: string;
  lote?: string;
  qtd: number;
  unidade: string;
  validade?: string;
  criado_em?: string;
}

export interface EventoFila {
  id: UUID;
  type: string;
  url: string;
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  headers?: Record<string,string>;
  body?: any;
  idempotencyKey: string;
  updatedAt: string; // ISO
  attempts?: number;
  lastError?: string;
}
