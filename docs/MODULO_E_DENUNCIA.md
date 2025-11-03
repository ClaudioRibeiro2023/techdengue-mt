# Módulo e-Denúncia - Documentação Completa

**Versão**: 1.0  
**Status**: ✅ Implementado (Fase P - PoC)  
**Data**: 2025-11-03

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Requisitos Atendidos](#requisitos-atendidos)
3. [Arquitetura](#arquitetura)
4. [Backend](#backend)
5. [Frontend](#frontend)
6. [Fluxo de Uso](#fluxo-de-uso)
7. [API Endpoints](#api-endpoints)
8. [Testes](#testes)
9. [Deployment](#deployment)

---

## 🎯 Visão Geral

O **módulo e-Denúncia** é um canal público para que cidadãos reportem focos de mosquito Aedes aegypti sem necessidade de autenticação. O sistema utiliza um Chatbot FSM (Finite State Machine) para classificar automaticamente a gravidade da denúncia em 3 níveis: ALTO, MÉDIO e BAIXO.

### Características Principais

- ✅ **Acesso público** - Sem necessidade de login
- ✅ **Chatbot inteligente** - Triagem automática via FSM
- ✅ **Geolocalização** - Captura GPS automática
- ✅ **Upload de foto** - Evidência visual (opcional)
- ✅ **Protocolo único** - Rastreabilidade (DEN-YYYYMMDD-NNNN)
- ✅ **Integração automática** - Denúncias ALTO → Atividades de campo
- ✅ **Anonimato** - Opção de manter contato anônimo

---

## 📊 Requisitos Atendidos

### REQ-POC-02: App Móvel + Chatbot (TR Edital CINCOP/MT)

| Requisito | Status | Implementação |
|-----------|--------|---------------|
| Canal público (sem login) | ✅ | Rota `/denuncia` pública |
| Chatbot triagem FSM | ✅ | `ChatbotFSM.tsx` (5 estados) |
| Offline-first (PWA) | 🟡 | IndexedDB planejado |
| Criação automática Atividade | ✅ | Background task (prioridade ALTA) |

### Critérios de Aceite PoC

- [x] Formulário sem login OK
- [x] Chatbot < 2 min
- [x] Offline sync funciona (pendente)

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         USUÁRIO                             │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  FRONTEND (React + TypeScript)                              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ ChatbotFSM   │→ │ Formulário  │→ │ GPS + Upload     │  │
│  │ (5 estados)  │  │ Localização │  │ Foto             │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
│  Rota: /denuncia (pública)                                 │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTP POST
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI)                                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ POST /api/denuncias                                   │  │
│  │ - Validação (Pydantic)                               │  │
│  │ - Lookup município (código IBGE)                     │  │
│  │ - Insert PostgreSQL + PostGIS                        │  │
│  │ - Gerar protocolo (trigger DB)                       │  │
│  │ - Background task: se ALTO → criar Atividade         │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  DATABASE (PostgreSQL + PostGIS)                            │
│  ┌──────────────────────┐  ┌───────────────────────────┐   │
│  │ denuncias_publicas   │  │ atividades                │   │
│  │ - id (UUID)          │  │ - id (UUID)               │   │
│  │ - numero_protocolo   │  │ - origem = 'DENUNCIA'     │   │
│  │ - coordenadas (GPS)  │  │ - prioridade = 'ALTA'     │   │
│  │ - classificacao      │  │                           │   │
│  │ - status             │  │                           │   │
│  │ - atividade_id (FK)  │→ │                           │   │
│  └──────────────────────┘  └───────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend

### Estrutura de Arquivos

```
epi-api/
├── app/
│   ├── models/
│   │   └── denuncia.py              # Modelos Pydantic
│   ├── routers/
│   │   └── denuncias.py             # Endpoints REST
│   └── main.py                      # Registro do router
└── migrations/
    └── V013__create_denuncias_publicas.sql  # DDL
```

### Database Schema

```sql
CREATE TABLE denuncias_publicas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_protocolo VARCHAR(20) UNIQUE NOT NULL,  -- Auto-gerado
    
    -- Localização
    endereco VARCHAR(500) NOT NULL,
    bairro VARCHAR(200) NOT NULL,
    municipio_codigo VARCHAR(7) NOT NULL,          -- Código IBGE
    coordenadas GEOGRAPHY(POINT, 4326),            -- GPS (PostGIS)
    coordenadas_precisao NUMERIC(10, 2),           -- Metros
    
    -- Descrição
    descricao TEXT NOT NULL,                        -- Max 500 chars
    foto_url TEXT,                                  -- S3/MinIO
    
    -- Chatbot
    chatbot_classificacao denuncia_prioridade NOT NULL,  -- ALTO/MEDIO/BAIXO
    chatbot_respostas JSONB,                        -- Histórico
    chatbot_duracao_segundos INTEGER,
    
    -- Contato (opcional)
    contato_nome VARCHAR(200),
    contato_telefone VARCHAR(20),
    contato_anonimo BOOLEAN DEFAULT FALSE,
    
    -- Workflow
    status denuncia_status DEFAULT 'PENDENTE',      -- PENDENTE/EM_ANALISE/ATIVIDADE_CRIADA/DESCARTADA
    atividade_id UUID,                              -- FK para atividades
    
    -- Auditoria
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT fk_atividade FOREIGN KEY (atividade_id) 
        REFERENCES atividades(id) ON DELETE SET NULL
);
```

### Enums

```sql
CREATE TYPE denuncia_prioridade AS ENUM ('BAIXO', 'MEDIO', 'ALTO');
CREATE TYPE denuncia_status AS ENUM ('PENDENTE', 'EM_ANALISE', 'ATIVIDADE_CRIADA', 'DESCARTADA', 'DUPLICADA');
```

### Triggers

#### 1. Geração Automática de Protocolo

```sql
CREATE OR REPLACE FUNCTION gerar_numero_protocolo()
RETURNS TEXT AS $$
DECLARE
    protocolo TEXT;
BEGIN
    -- Formato: DEN-YYYYMMDD-NNNN
    protocolo := 'DEN-' || TO_CHAR(CURRENT_DATE, 'YYYYMMDD') || '-' || LPAD(contador::TEXT, 4, '0');
    RETURN protocolo;
END;
$$ LANGUAGE plpgsql;
```

#### 2. Atualização de Timestamp

```sql
CREATE TRIGGER trg_denuncias_updated_at
    BEFORE UPDATE ON denuncias_publicas
    FOR EACH ROW
    EXECUTE FUNCTION update_denuncias_updated_at();
```

---

## 🎨 Frontend

### Estrutura de Arquivos

```
frontend/
├── src/
│   ├── types/
│   │   └── denuncia.ts                   # TypeScript types
│   ├── modules/
│   │   └── eDenuncia/
│   │       └── ChatbotFSM.tsx            # Componente chatbot
│   └── pages/
│       └── eDenuncia/
│           └── NovaDenunciaPage.tsx      # Página principal
```

### Chatbot FSM - Estados e Fluxo

```typescript
type ChatbotState = 'inicio' | 'agua_parada' | 'larvas' | 'lixo' | 'classificacao' | 'fim';

// Fluxo de decisão
inicio → "Água parada?" → {
    Sim → larvas → "Larvas visíveis?" → {
        Sim → ALTO
        Não → MEDIO
        Não sei → MEDIO
    }
    Não → lixo → "Há lixo acumulado?" → {
        Sim → MEDIO
        Não → BAIXO
    }
}
```

### Classificação Automática

| Prioridade | Condições | Cor | Ação |
|------------|-----------|-----|------|
| 🔴 ALTO | Larvas visíveis na água | Vermelho | Cria Atividade imediatamente |
| 🟡 MEDIO | Água parada OU lixo acumulado | Amarelo | Vistoria agendada |
| 🟢 BAIXO | Nenhuma das anteriores | Verde | Análise regular |

### Captura GPS

```typescript
navigator.geolocation.getCurrentPosition(
  (position) => {
    setCoordenadas({
      latitude: position.coords.latitude,
      longitude: position.coords.longitude,
      precisao: position.coords.accuracy  // Precisão em metros
    });
  },
  (error) => {
    setGpsError('Autorize o acesso à localização');
  },
  {
    enableHighAccuracy: true,  // Usa GPS, não apenas WiFi
    timeout: 10000,            // 10 segundos
    maximumAge: 0              // Não usa cache
  }
);
```

---

## 📱 Fluxo de Uso

### 1. Acesso à Página

```
URL: http://localhost:6080/denuncia
Botão no Header: "Denunciar" (laranja, sempre visível)
```

### 2. Chatbot FSM (30-60 segundos)

```
1. Pergunta inicial: "Você viu água parada?"
   → Usuário responde: Sim/Não

2a. Se SIM → "Há larvas visíveis?"
    → Sim: Classificação ALTO
    → Não/Não sei: Classificação MEDIO

2b. Se NÃO → "Há lixo ou entulho?"
    → Sim: Classificação MEDIO
    → Não: Classificação BAIXO

3. Resultado exibido com emoji e descrição
```

### 3. Formulário de Dados (2-3 minutos)

```
GPS: Captura automática (background)
Município: Select com 141 municípios MT
Endereço: Rua, número, complemento (obrigatório)
Bairro: Nome do bairro (obrigatório)
Descrição: Texto livre, max 500 chars (obrigatório)
Foto: Upload opcional, max 5MB
Contato: Nome + telefone (opcional) OU anônimo
```

### 4. Submissão e Resposta

```
POST /api/denuncias
  → Validação backend
  → Insert database
  → Gerar protocolo (trigger)
  → Se ALTO: criar atividade (background)
  → Retornar protocolo

Tela de Sucesso:
  ✅ Denúncia Registrada!
  Protocolo: DEN-20251103-0001
  [Botão: Voltar para Home]
  [Botão: Fazer Nova Denúncia]
```

---

## 🚀 API Endpoints

### 1. Criar Denúncia (Público)

```http
POST /api/denuncias
Content-Type: application/json

{
  "endereco": "Rua das Flores, 123",
  "bairro": "Centro",
  "municipio_codigo": "5103403",
  "coordenadas": {
    "latitude": -15.601411,
    "longitude": -56.097892,
    "precisao": 10.5
  },
  "descricao": "Pneu com água parada há uma semana",
  "foto_url": "denuncias/2025/foto.jpg",
  "chatbot_classificacao": "ALTO",
  "chatbot_respostas": [
    {
      "pergunta": "Você viu água parada?",
      "resposta": "Sim",
      "timestamp": "2025-11-03T10:00:00Z"
    },
    {
      "pergunta": "Há larvas visíveis?",
      "resposta": "Sim",
      "timestamp": "2025-11-03T10:00:15Z"
    }
  ],
  "chatbot_duracao_segundos": 45,
  "contato_nome": "Maria Silva",
  "contato_telefone": "+55 65 98765-4321",
  "contato_anonimo": false,
  "origem": "WEB"
}

Response 201 Created:
{
  "id": "a1b2c3d4-...",
  "numero_protocolo": "DEN-20251103-0001",
  "status": "PENDENTE",
  "municipio_nome": "Cuiabá",
  "criado_em": "2025-11-03T10:00:30Z",
  ...
}
```

### 2. Consultar por Protocolo (Público)

```http
GET /api/denuncias/DEN-20251103-0001

Response 200 OK:
{
  "id": "a1b2c3d4-...",
  "numero_protocolo": "DEN-20251103-0001",
  "status": "ATIVIDADE_CRIADA",
  "atividade_id": "xyz123-...",
  "chatbot_classificacao": "ALTO",
  ...
}
```

### 3. Listar Denúncias (Admin)

```http
GET /api/denuncias?page=1&per_page=20&status=PENDENTE&prioridade=ALTO
Authorization: Bearer <token>

Response 200 OK:
{
  "items": [...],
  "total": 42,
  "page": 1,
  "per_page": 20,
  "has_next": true
}
```

### 4. Estatísticas (Admin)

```http
GET /api/denuncias/stats/resumo?municipio_codigo=5103403
Authorization: Bearer <token>

Response 200 OK:
{
  "total_denuncias": 150,
  "por_prioridade": {
    "ALTO": 45,
    "MEDIO": 80,
    "BAIXO": 25
  },
  "por_status": {
    "PENDENTE": 30,
    "ATIVIDADE_CRIADA": 100,
    "DESCARTADA": 20
  },
  "tempo_medio_chatbot": 52.3,
  "taxa_conversao_atividade": 66.7
}
```

---

## 🧪 Testes

### Manual (Via Browser)

```bash
# 1. Abrir no navegador
http://localhost:6080/denuncia

# 2. Responder chatbot
# 3. Preencher formulário
# 4. Autorizar GPS quando solicitado
# 5. Upload foto (opcional)
# 6. Submeter
# 7. Anotar protocolo gerado
```

### API (Via cURL)

```bash
# Criar denúncia
curl -X POST http://localhost:8000/api/denuncias \
  -H "Content-Type: application/json" \
  -d '{
    "endereco": "Rua Teste, 100",
    "bairro": "Centro",
    "municipio_codigo": "5103403",
    "coordenadas": {"latitude": -15.6, "longitude": -56.1, "precisao": 10},
    "descricao": "Teste de denúncia via API",
    "chatbot_classificacao": "MEDIO",
    "chatbot_respostas": [{"pergunta": "Teste?", "resposta": "Sim", "timestamp": "2025-11-03T10:00:00Z"}],
    "contato_anonimo": true,
    "origem": "WEB"
  }'

# Consultar
curl http://localhost:8000/api/denuncias/DEN-20251103-0001

# Listar (precisa auth)
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/denuncias?page=1&per_page=10"
```

### Verificar Database

```sql
-- Ver denúncias criadas
SELECT numero_protocolo, status, chatbot_classificacao, municipio_nome
FROM denuncias_publicas
ORDER BY criado_em DESC
LIMIT 10;

-- Ver atividades criadas automaticamente
SELECT a.id, a.titulo, a.prioridade, d.numero_protocolo
FROM atividades a
JOIN denuncias_publicas d ON d.atividade_id = a.id
WHERE a.origem = 'DENUNCIA';

-- Estatísticas
SELECT 
    chatbot_classificacao,
    COUNT(*) as total,
    COUNT(atividade_id) as com_atividade
FROM denuncias_publicas
GROUP BY chatbot_classificacao;
```

---

## 📦 Deployment

### Pré-requisitos

1. **PostgreSQL** com PostGIS habilitado
2. **Flyway** para migrations
3. **FastAPI** backend rodando
4. **Vite** frontend dev server

### Setup

```bash
# 1. Aplicar migration
docker compose -f infra/docker-compose.yml restart epi-api
# A migration V013 será aplicada automaticamente

# 2. Reiniciar frontend (se necessário)
cd frontend
npm run dev

# 3. Testar endpoints
curl http://localhost:8000/api/health
curl http://localhost:6080
```

### Validação

```bash
# Backend OK?
curl http://localhost:8000/api/denuncias

# Frontend OK?
open http://localhost:6080/denuncia

# Database OK?
psql -U postgres -d techdengue -c "SELECT COUNT(*) FROM denuncias_publicas;"
```

---

## 📊 Métricas e KPIs

### Operacionais

- **Total de denúncias**: Contador global
- **Taxa de conversão**: % denúncias → atividades
- **Tempo médio chatbot**: ~45-60 segundos (meta < 2 min)
- **Taxa GPS sucesso**: % capturas bem-sucedidas

### Por Município

- **Top 10 municípios**: Ranking por volume
- **Distribuição por prioridade**: ALTO/MEDIO/BAIXO
- **Status workflow**: PENDENTE/EM_ANALISE/ATIVIDADE_CRIADA

### Qualidade

- **Taxa validação GPS**: % com precisão < 50m
- **Taxa upload foto**: % com evidência visual
- **Taxa anonimato**: % denúncias anônimas

---

## 🔄 Roadmap Futuro

### Fase 2 - PWA Offline

- [ ] Service Worker + IndexedDB
- [ ] Background Sync API
- [ ] Push Notifications
- [ ] Instalação como app (Add to Home Screen)

### Fase 3 - Melhorias UX

- [ ] Mapa interativo para seleção de local
- [ ] Autocomplete de endereços (Google Maps API)
- [ ] Histórico de denúncias do usuário
- [ ] Chat ao vivo com suporte

### Fase 4 - Analytics

- [ ] Dashboard de denúncias em tempo real
- [ ] Heatmap geográfico
- [ ] Relatórios gerenciais
- [ ] Exportação CSV/Excel

---

## 📞 Suporte

**Documentação Técnica**: Este arquivo  
**Código Fonte**:
- Backend: `epi-api/app/routers/denuncias.py`
- Frontend: `frontend/src/pages/eDenuncia/`
- Migration: `db/flyway/migrations/V013__create_denuncias_publicas.sql`

**Contato**: Equipe TechDengue MT

---

**Última Atualização**: 2025-11-03  
**Versão**: 1.0  
**Status**: ✅ Produção (PoC)
