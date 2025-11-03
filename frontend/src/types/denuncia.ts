/**
 * Tipos TypeScript para Denúncias Públicas (e-Denúncia)
 * Módulo PoC - Fase P (ELIMINATÓRIA)
 */

export type DenunciaStatus =
  | 'PENDENTE'
  | 'EM_ANALISE'
  | 'ATIVIDADE_CRIADA'
  | 'DESCARTADA'
  | 'DUPLICADA';

export type DenunciaPrioridade = 'BAIXO' | 'MEDIO' | 'ALTO';

export interface CoordenadasGPS {
  latitude: number;
  longitude: number;
  precisao?: number; // Precisão em metros
}

export interface ChatbotResposta {
  pergunta: string;
  resposta: string;
  timestamp: string;
}

export interface DenunciaCreate {
  // Localização
  endereco: string;
  bairro: string;
  municipio_codigo: string;
  coordenadas: CoordenadasGPS;
  
  // Descrição
  descricao: string;
  foto_url?: string;
  
  // Chatbot
  chatbot_classificacao: DenunciaPrioridade;
  chatbot_respostas: ChatbotResposta[];
  chatbot_duracao_segundos?: number;
  
  // Contato (opcional)
  contato_nome?: string;
  contato_telefone?: string;
  contato_email?: string;
  contato_anonimo: boolean;
  
  // Metadata
  origem: 'WEB' | 'PWA' | 'APP';
  user_agent?: string;
}

export interface DenunciaResponse {
  id: string;
  numero_protocolo: string;
  endereco: string;
  bairro: string;
  municipio_codigo: string;
  municipio_nome?: string;
  coordenadas?: CoordenadasGPS;
  descricao: string;
  foto_url?: string;
  chatbot_classificacao: DenunciaPrioridade;
  chatbot_duracao_segundos?: number;
  contato_nome?: string;
  contato_telefone?: string;
  contato_anonimo: boolean;
  status: DenunciaStatus;
  atividade_id?: string;
  criado_em: string;
  atualizado_em: string;
  sincronizado_em?: string;
}

// Para IndexedDB (offline storage)
export interface DenunciaOffline {
  id: string; // UUID local
  timestamp: number;
  status: 'pending' | 'syncing' | 'synced' | 'error';
  form: DenunciaCreate;
  retry_count: number;
  error_message?: string;
}
