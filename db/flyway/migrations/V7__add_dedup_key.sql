-- V7: Add dedup_key for idempotent ETL inserts
-- Adds a nullable dedup_key and a partial UNIQUE index to prevent duplicate rows

ALTER TABLE indicador_epi ADD COLUMN IF NOT EXISTS dedup_key TEXT;

-- Unique index must include partitioning column (competencia) for hypertables
CREATE UNIQUE INDEX IF NOT EXISTS ux_indicador_epi_comp_dedup
ON indicador_epi (competencia, dedup_key)
WHERE dedup_key IS NOT NULL;
