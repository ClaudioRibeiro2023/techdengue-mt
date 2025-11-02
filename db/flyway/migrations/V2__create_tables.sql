-- Minimal tables (no geometry columns to avoid PostGIS dependency)
CREATE TABLE IF NOT EXISTS indicador_epi (
  id BIGSERIAL,
  competencia DATE NOT NULL,
  municipio_cod_ibge VARCHAR(7),
  indicador TEXT NOT NULL,
  valor NUMERIC,
  PRIMARY KEY (competencia, id)
);

-- Timescale hypertable on competencia
SELECT create_hypertable('indicador_epi', 'competencia', if_not_exists => TRUE);

CREATE TABLE IF NOT EXISTS atividade (
  id BIGSERIAL PRIMARY KEY,
  status atividade_status NOT NULL DEFAULT 'CRIADA',
  origem atividade_origem NOT NULL DEFAULT 'MANUAL',
  municipio_cod_ibge VARCHAR(7),
  criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS evidencia (
  id BIGSERIAL PRIMARY KEY,
  atividade_id BIGINT REFERENCES atividade(id) ON DELETE CASCADE,
  hash_sha256 TEXT NOT NULL,
  url TEXT,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS relatorio (
  id BIGSERIAL PRIMARY KEY,
  tipo TEXT NOT NULL,
  caminho TEXT NOT NULL,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS audit_log (
  id BIGSERIAL PRIMARY KEY,
  usuario TEXT,
  acao TEXT NOT NULL,
  recurso TEXT NOT NULL,
  detalhes JSONB DEFAULT '{}'::jsonb,
  criado_em TIMESTAMPTZ NOT NULL DEFAULT now()
);
