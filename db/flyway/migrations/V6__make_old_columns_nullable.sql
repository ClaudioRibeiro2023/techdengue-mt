-- V6: Make legacy columns (indicador, valor) nullable
-- These columns were from V2 but are no longer used in ETL imports
-- All data is now in the detailed columns added in V5

ALTER TABLE indicador_epi ALTER COLUMN indicador DROP NOT NULL;
ALTER TABLE indicador_epi ALTER COLUMN valor DROP NOT NULL;

-- Add comments to document the change
COMMENT ON COLUMN indicador_epi.indicador IS 'Legacy column from V2, nullable since V6. Detailed data in specific columns.';
COMMENT ON COLUMN indicador_epi.valor IS 'Legacy column from V2, nullable since V6. Detailed data in specific columns.';
