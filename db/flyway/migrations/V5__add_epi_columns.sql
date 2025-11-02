-- V5: Add detailed EPI columns for ETL import
-- Adds all fields from CSV-EPI01 format

-- Add demographic columns
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dt_sintomas DATE;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dt_notificacao DATE;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS sexo VARCHAR(1);
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS idade INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS faixa_etaria VARCHAR(10);
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS gestante VARCHAR(1);

-- Add classification columns
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS classificacao_final VARCHAR(50);
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS criterio_confirmacao VARCHAR(50);

-- Add symptoms/signs columns (binary 0/1)
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS febre INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS cefaleia INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dor_retroocular INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS mialgia INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS artralgia INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS exantema INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS vomito INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS nausea INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dor_abdominal INTEGER;

-- Add alarm signs columns (binary 0/1)
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS plaquetas_baixas INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS hemorragia INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS hepatomegalia INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS acumulo_liquidos INTEGER;

-- Add comorbidities columns (binary 0/1)
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS diabetes INTEGER;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS hipertensao INTEGER;

-- Add outcome columns
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS evolucao VARCHAR(50);
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dt_obito DATE;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dt_encerramento DATE;

-- Add audit columns
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS arquivo_origem TEXT;
ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dt_importacao TIMESTAMP;

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_indicador_epi_dt_sintomas ON indicador_epi(dt_sintomas);
CREATE INDEX IF NOT EXISTS idx_indicador_epi_municipio ON indicador_epi(municipio_cod_ibge);
CREATE INDEX IF NOT EXISTS idx_indicador_epi_classificacao ON indicador_epi(classificacao_final);
CREATE INDEX IF NOT EXISTS idx_indicador_epi_evolucao ON indicador_epi(evolucao);
CREATE INDEX IF NOT EXISTS idx_indicador_epi_dt_importacao ON indicador_epi(dt_importacao);
