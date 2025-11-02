-- V11: Add ETL jobs tracking table
-- Data: 2024-11-02
-- Descrição: Tabela para tracking de jobs ETL (SINAN e LIRAa)

-- ============================================================================
-- ETL Jobs Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS etl_jobs (
    -- Identificação
    job_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source VARCHAR(20) NOT NULL CHECK (source IN ('SINAN', 'LIRAA', 'MANUAL')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED', 'PARTIAL')),
    
    -- Arquivo
    file_path TEXT NOT NULL,
    
    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Progress tracking
    total_rows INTEGER,
    processed_rows INTEGER DEFAULT 0,
    success_rows INTEGER DEFAULT 0,
    error_rows INTEGER DEFAULT 0,
    
    -- Errors
    error_message TEXT,
    error_details JSONB,
    
    -- Metadata adicional
    metadata JSONB DEFAULT '{}',
    
    -- Índices
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Índices para performance
CREATE INDEX idx_etl_jobs_status ON etl_jobs(status);
CREATE INDEX idx_etl_jobs_source ON etl_jobs(source);
CREATE INDEX idx_etl_jobs_started_at ON etl_jobs(started_at DESC);
CREATE INDEX idx_etl_jobs_source_status ON etl_jobs(source, status);

-- Trigger para atualizar updated_at
CREATE OR REPLACE FUNCTION update_etl_jobs_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_etl_jobs_updated_at
    BEFORE UPDATE ON etl_jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_etl_jobs_updated_at();

-- ============================================================================
-- Comentários
-- ============================================================================

COMMENT ON TABLE etl_jobs IS 'Tracking de jobs ETL (importação SINAN e LIRAa)';
COMMENT ON COLUMN etl_jobs.job_id IS 'ID único do job ETL';
COMMENT ON COLUMN etl_jobs.source IS 'Fonte dos dados (SINAN, LIRAa, Manual)';
COMMENT ON COLUMN etl_jobs.status IS 'Status atual do job';
COMMENT ON COLUMN etl_jobs.file_path IS 'Caminho do arquivo CSV (local ou S3)';
COMMENT ON COLUMN etl_jobs.total_rows IS 'Total de linhas no CSV';
COMMENT ON COLUMN etl_jobs.processed_rows IS 'Linhas processadas até o momento';
COMMENT ON COLUMN etl_jobs.success_rows IS 'Linhas processadas com sucesso';
COMMENT ON COLUMN etl_jobs.error_rows IS 'Linhas com erro';
COMMENT ON COLUMN etl_jobs.error_details IS 'Detalhes dos erros (JSON array)';
COMMENT ON COLUMN etl_jobs.metadata IS 'Metadata adicional do job (doenca_tipo, ano, etc)';
