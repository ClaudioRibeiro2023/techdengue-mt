-- V014__create_atividades_min.sql
-- Cria tabelas mínimas para suportar criação de atividades a partir de denúncias

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS postgis;

-- Tabela de atividades
CREATE TABLE IF NOT EXISTS atividades (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo VARCHAR(300) NOT NULL,
    descricao TEXT,
    tipo VARCHAR(50) NOT NULL,                -- e.g., 'VISITA'
    prioridade VARCHAR(20) NOT NULL,          -- e.g., 'ALTA', 'MEDIA', 'BAIXA'
    status VARCHAR(30) NOT NULL DEFAULT 'PENDENTE',

    municipio_codigo VARCHAR(7),              -- IBGE 7 dígitos
    endereco VARCHAR(500),
    coordenadas GEOGRAPHY(POINT, 4326),

    origem VARCHAR(30),                       -- e.g., 'DENUNCIA'

    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Índices úteis
CREATE INDEX IF NOT EXISTS idx_atividades_status ON atividades(status) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_atividades_municipio ON atividades(municipio_codigo) WHERE deleted_at IS NULL;

-- Tabela de evidências de atividades (ex.: fotos)
CREATE TABLE IF NOT EXISTS atividade_evidencias (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    atividade_id UUID NOT NULL,
    tipo VARCHAR(30) NOT NULL,                -- e.g., 'FOTO'
    arquivo_url TEXT NOT NULL,
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,

    CONSTRAINT fk_atividade_evidencia
        FOREIGN KEY (atividade_id)
        REFERENCES atividades(id)
        ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_atividade_evidencias_atividade ON atividade_evidencias(atividade_id);
