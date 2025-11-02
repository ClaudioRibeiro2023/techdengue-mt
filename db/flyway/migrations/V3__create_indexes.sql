-- Indexes
CREATE INDEX IF NOT EXISTS idx_indicador_epi_competencia ON indicador_epi (competencia DESC);
CREATE INDEX IF NOT EXISTS idx_atividade_status_municipio ON atividade (status, municipio_cod_ibge);
CREATE INDEX IF NOT EXISTS idx_atividade_criado_em ON atividade (criado_em DESC);
