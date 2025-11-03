-- V013: Criação da tabela denuncias_publicas para módulo e-Denúncia
-- Permite cidadãos reportarem focos de Aedes aegypti sem login obrigatório
-- Integra com chatbot FSM para triagem e classificação de prioridade

-- Extensões necessárias (provavelmente já existem, mas garantindo)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- Enum para status da denúncia
CREATE TYPE denuncia_status AS ENUM (
    'PENDENTE',           -- Aguardando análise
    'EM_ANALISE',         -- Sendo verificada
    'ATIVIDADE_CRIADA',   -- Convertida em atividade de campo
    'DESCARTADA',         -- Não procede
    'DUPLICADA'           -- Denúncia duplicada
);

-- Enum para classificação de prioridade (saída do chatbot)
CREATE TYPE denuncia_prioridade AS ENUM (
    'BAIXO',
    'MEDIO',
    'ALTO'
);

-- Tabela principal de denúncias públicas
CREATE TABLE denuncias_publicas (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero_protocolo VARCHAR(20) UNIQUE NOT NULL,  -- Formato: DEN-YYYYMMDD-NNNN
    
    -- Localização
    endereco VARCHAR(500) NOT NULL,
    bairro VARCHAR(200) NOT NULL,
    municipio_codigo VARCHAR(7) NOT NULL,          -- Código IBGE 7 dígitos
    municipio_nome VARCHAR(200),                    -- Preenchido via lookup
    coordenadas GEOGRAPHY(POINT, 4326),            -- GPS capturado
    coordenadas_precisao NUMERIC(10, 2),           -- Precisão em metros
    
    -- Descrição do problema
    descricao TEXT NOT NULL,                        -- Max 500 chars (validado no backend)
    foto_url TEXT,                                  -- S3 object key
    foto_hash VARCHAR(64),                          -- SHA-256 da foto (integridade)
    
    -- Triagem via Chatbot FSM
    chatbot_classificacao denuncia_prioridade NOT NULL,
    chatbot_respostas JSONB,                        -- Array de respostas do usuário
    chatbot_duracao_segundos INTEGER,               -- Tempo gasto no chatbot
    
    -- Contato (opcional - anonimato permitido)
    contato_nome VARCHAR(200),
    contato_telefone VARCHAR(20),
    contato_email VARCHAR(200),
    contato_anonimo BOOLEAN DEFAULT FALSE,
    
    -- Status e workflow
    status denuncia_status DEFAULT 'PENDENTE' NOT NULL,
    atividade_id UUID,                              -- FK para atividades (se criada)
    motivo_descarte TEXT,                           -- Se status = DESCARTADA
    
    -- Metadata
    criado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    atualizado_em TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    sincronizado_em TIMESTAMP WITH TIME ZONE,       -- Timestamp do sync offline
    origem VARCHAR(20) DEFAULT 'WEB',               -- WEB, PWA, APP
    user_agent TEXT,                                -- Captura para analytics
    ip_origem INET,                                 -- IP do solicitante
    
    -- Auditoria
    analisado_por_user_id VARCHAR(100),            -- Keycloak user_id
    analisado_em TIMESTAMP WITH TIME ZONE,
    
    -- Soft delete
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    -- FK para atividades será adicionada em migration futura quando tabela existir
    -- CONSTRAINT fk_atividade 
    --     FOREIGN KEY (atividade_id) 
    --     REFERENCES atividades(id) 
    --     ON DELETE SET NULL,
    
    CONSTRAINT check_coordenadas_precisao 
        CHECK (coordenadas_precisao IS NULL OR coordenadas_precisao >= 0),
    
    CONSTRAINT check_descricao_length 
        CHECK (char_length(descricao) <= 500)
);

-- Índices para performance
CREATE INDEX idx_denuncias_status ON denuncias_publicas(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_denuncias_municipio ON denuncias_publicas(municipio_codigo) WHERE deleted_at IS NULL;
CREATE INDEX idx_denuncias_criado_em ON denuncias_publicas(criado_em DESC) WHERE deleted_at IS NULL;
CREATE INDEX idx_denuncias_prioridade ON denuncias_publicas(chatbot_classificacao) WHERE deleted_at IS NULL;
CREATE INDEX idx_denuncias_atividade ON denuncias_publicas(atividade_id) WHERE atividade_id IS NOT NULL;
CREATE INDEX idx_denuncias_protocolo ON denuncias_publicas(numero_protocolo);

-- Índice espacial para queries geográficas
CREATE INDEX idx_denuncias_coordenadas ON denuncias_publicas USING GIST(coordenadas) WHERE coordenadas IS NOT NULL;

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_denuncias_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_denuncias_updated_at
    BEFORE UPDATE ON denuncias_publicas
    FOR EACH ROW
    EXECUTE FUNCTION update_denuncias_updated_at();

-- Função para gerar número de protocolo automático
CREATE OR REPLACE FUNCTION gerar_numero_protocolo()
RETURNS TEXT AS $$
DECLARE
    data_atual DATE := CURRENT_DATE;
    contador INTEGER;
    protocolo TEXT;
BEGIN
    -- Conta denúncias do dia
    SELECT COUNT(*) INTO contador
    FROM denuncias_publicas
    WHERE DATE(criado_em) = data_atual;
    
    -- Formata protocolo: DEN-YYYYMMDD-NNNN
    protocolo := 'DEN-' || TO_CHAR(data_atual, 'YYYYMMDD') || '-' || LPAD((contador + 1)::TEXT, 4, '0');
    
    RETURN protocolo;
END;
$$ LANGUAGE plpgsql;

-- Trigger para gerar protocolo automaticamente
CREATE OR REPLACE FUNCTION set_numero_protocolo()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.numero_protocolo IS NULL THEN
        NEW.numero_protocolo = gerar_numero_protocolo();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_numero_protocolo
    BEFORE INSERT ON denuncias_publicas
    FOR EACH ROW
    EXECUTE FUNCTION set_numero_protocolo();

-- View para estatísticas de denúncias
CREATE OR REPLACE VIEW vw_denuncias_stats AS
SELECT 
    municipio_codigo,
    municipio_nome,
    status,
    chatbot_classificacao,
    COUNT(*) as total,
    COUNT(CASE WHEN atividade_id IS NOT NULL THEN 1 END) as com_atividade,
    AVG(chatbot_duracao_segundos) as tempo_medio_chatbot,
    MAX(criado_em) as ultima_denuncia
FROM denuncias_publicas
WHERE deleted_at IS NULL
GROUP BY municipio_codigo, municipio_nome, status, chatbot_classificacao;

-- Comentários para documentação
COMMENT ON TABLE denuncias_publicas IS 'Denúncias públicas de focos de Aedes aegypti via módulo e-Denúncia';
COMMENT ON COLUMN denuncias_publicas.numero_protocolo IS 'Protocolo único formato DEN-YYYYMMDD-NNNN gerado automaticamente';
COMMENT ON COLUMN denuncias_publicas.chatbot_classificacao IS 'Prioridade definida pelo chatbot FSM: ALTO (larvas visíveis), MEDIO (água parada), BAIXO (lixo)';
COMMENT ON COLUMN denuncias_publicas.chatbot_respostas IS 'Histórico de respostas do usuário no chatbot em formato JSON';
COMMENT ON COLUMN denuncias_publicas.atividade_id IS 'FK para atividade de campo criada a partir desta denúncia';
COMMENT ON COLUMN denuncias_publicas.coordenadas IS 'Coordenadas GPS capturadas automaticamente (POINT com SRID 4326)';
