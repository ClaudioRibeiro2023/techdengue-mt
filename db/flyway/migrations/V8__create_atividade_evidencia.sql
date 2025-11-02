-- V8: Create atividade and evidencia tables for Campo API (M2)

-- Atividade table (already partially exists from V2, extend it)
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS tipo VARCHAR(50);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS origem VARCHAR(50) NOT NULL DEFAULT 'MANUAL';
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS municipio_nome VARCHAR(255);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS localizacao_lon NUMERIC(10, 7);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS localizacao_lat NUMERIC(10, 7);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS localizacao_alt NUMERIC(10, 2);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS descricao TEXT;
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS iniciado_em TIMESTAMPTZ;
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS encerrado_em TIMESTAMPTZ;
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS usuario_criacao VARCHAR(255);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS usuario_responsavel VARCHAR(255);
ALTER TABLE atividade ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMPTZ DEFAULT now();

-- Add indexes for atividade
CREATE INDEX IF NOT EXISTS idx_atividade_status ON atividade(status);
CREATE INDEX IF NOT EXISTS idx_atividade_tipo ON atividade(tipo);
CREATE INDEX IF NOT EXISTS idx_atividade_municipio ON atividade(municipio_cod_ibge);
CREATE INDEX IF NOT EXISTS idx_atividade_origem ON atividade(origem);
CREATE INDEX IF NOT EXISTS idx_atividade_criado_em ON atividade(criado_em);
CREATE INDEX IF NOT EXISTS idx_atividade_localizacao ON atividade(localizacao_lon, localizacao_lat);

-- Add GIN index for metadata JSONB
CREATE INDEX IF NOT EXISTS idx_atividade_metadata ON atividade USING GIN(metadata);

-- Update trigger for atualizado_em
CREATE OR REPLACE FUNCTION update_atividade_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_atividade_updated
BEFORE UPDATE ON atividade
FOR EACH ROW
EXECUTE FUNCTION update_atividade_timestamp();

-- Evidencia table (extend existing from V2)
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS tipo VARCHAR(50);
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'PENDENTE';
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS tamanho_bytes BIGINT;
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS descricao TEXT;
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS url_download TEXT;
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS upload_id VARCHAR(255);
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS atualizado_em TIMESTAMPTZ DEFAULT now();

-- Rename 'url' to 'url_s3' for clarity
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'evidencia' AND column_name = 'url'
    ) THEN
        ALTER TABLE evidencia RENAME COLUMN url TO url_s3;
    END IF;
END $$;

-- Add url_s3 if it doesn't exist
ALTER TABLE evidencia ADD COLUMN IF NOT EXISTS url_s3 TEXT;

-- Add indexes for evidencia
CREATE INDEX IF NOT EXISTS idx_evidencia_atividade ON evidencia(atividade_id);
CREATE INDEX IF NOT EXISTS idx_evidencia_tipo ON evidencia(tipo);
CREATE INDEX IF NOT EXISTS idx_evidencia_status ON evidencia(status);
CREATE INDEX IF NOT EXISTS idx_evidencia_hash ON evidencia(hash_sha256);
CREATE INDEX IF NOT EXISTS idx_evidencia_criado_em ON evidencia(criado_em);

-- GIN index for evidencia metadata
CREATE INDEX IF NOT EXISTS idx_evidencia_metadata ON evidencia USING GIN(metadata);

-- Update trigger for evidencia
CREATE OR REPLACE FUNCTION update_evidencia_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_evidencia_updated
BEFORE UPDATE ON evidencia
FOR EACH ROW
EXECUTE FUNCTION update_evidencia_timestamp();

-- Sync log table for offline synchronization
CREATE TABLE IF NOT EXISTS sync_log (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(255) NOT NULL,
    idempotency_key VARCHAR(36) NOT NULL,
    operation_type VARCHAR(50) NOT NULL,
    payload JSONB NOT NULL,
    success BOOLEAN DEFAULT FALSE,
    conflict BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    resource_id BIGINT,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Unique constraint for idempotency
CREATE UNIQUE INDEX IF NOT EXISTS ux_sync_log_idempotency 
ON sync_log(idempotency_key);

-- Indexes for sync_log
CREATE INDEX IF NOT EXISTS idx_sync_log_device ON sync_log(device_id);
CREATE INDEX IF NOT EXISTS idx_sync_log_operation ON sync_log(operation_type);
CREATE INDEX IF NOT EXISTS idx_sync_log_criado_em ON sync_log(criado_em);
CREATE INDEX IF NOT EXISTS idx_sync_log_success ON sync_log(success);

-- Comments for documentation
COMMENT ON TABLE atividade IS 'Field activities (vistorias, LIRAa, nebulização, etc)';
COMMENT ON TABLE evidencia IS 'Evidence/media attached to activities (photos, videos, documents)';
COMMENT ON TABLE sync_log IS 'Sync operations log for offline-first PWA';

COMMENT ON COLUMN atividade.tipo IS 'VISTORIA, LIRAA, NEBULIZACAO, ARMADILHA, etc';
COMMENT ON COLUMN atividade.origem IS 'MANUAL, IMPORTACAO, ALERTA';
COMMENT ON COLUMN atividade.status IS 'CRIADA, EM_ANDAMENTO, CONCLUIDA, CANCELADA';
COMMENT ON COLUMN atividade.metadata IS 'Custom JSONB metadata for flexibility';

COMMENT ON COLUMN evidencia.tipo IS 'FOTO, VIDEO, DOCUMENTO, AUDIO';
COMMENT ON COLUMN evidencia.status IS 'PENDENTE, UPLOADING, CONCLUIDA, ERRO, DELETADA';
COMMENT ON COLUMN evidencia.hash_sha256 IS 'SHA-256 hash for integrity verification';
COMMENT ON COLUMN evidencia.metadata IS 'EXIF, geotag, watermark info, etc';
