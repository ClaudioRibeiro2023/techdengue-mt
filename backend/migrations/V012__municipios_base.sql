-- V012: Tabelas base de municípios MT (IBGE, geometrias, LIRAa)
-- Autor: Sistema TechDengue MT
-- Data: 2025-11-02
-- Objetivo: Carregar dados reais de municípios MT (141 total)

-- =========================================================================
-- 1. Tabela de dados IBGE (população, área, indicadores)
-- =========================================================================

CREATE TABLE IF NOT EXISTS municipios_ibge (
    codigo_ibge VARCHAR(7) PRIMARY KEY,  -- Ex: "5100102" (Acorizal)
    nome VARCHAR(100) NOT NULL,
    gentilico VARCHAR(100),
    prefeito_2025 VARCHAR(200),
    area_km2 NUMERIC(10,3),
    populacao_censo_2022 INTEGER,
    densidade_demografica NUMERIC(8,2),
    populacao_estimada_2025 INTEGER NOT NULL,  -- Para cálculo de incidência
    escolarizacao_6_14 NUMERIC(5,2),
    idhm_2010 NUMERIC(4,3),
    mortalidade_infantil_2023 NUMERIC(5,2),
    receitas_brutas_2024 NUMERIC(15,2),
    despesas_brutas_2024 NUMERIC(15,2),
    pib_per_capita_2021 NUMERIC(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_municipios_ibge_nome ON municipios_ibge(nome);
COMMENT ON TABLE municipios_ibge IS 'Dados IBGE dos 141 municípios de Mato Grosso';
COMMENT ON COLUMN municipios_ibge.codigo_ibge IS 'Código IBGE 7 dígitos (prefixo 51)';
COMMENT ON COLUMN municipios_ibge.populacao_estimada_2025 IS 'Usado para cálculo de incidência (casos/100k hab)';

-- =========================================================================
-- 2. Tabela de geometrias municipais (PostGIS)
-- =========================================================================

CREATE TABLE IF NOT EXISTS municipios_geometrias (
    codigo_ibge VARCHAR(7) PRIMARY KEY REFERENCES municipios_ibge(codigo_ibge),
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,  -- WGS84 (EPSG:4326) para Leaflet
    geom_simplificada GEOMETRY(MULTIPOLYGON, 4326),  -- Simplificada para zoom baixo
    centroide GEOMETRY(POINT, 4326),  -- Centro geométrico para labels
    area_calculada_km2 NUMERIC(10,3),  -- Área calculada do polígono
    perimetro_km NUMERIC(10,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Índices espaciais (GIST)
CREATE INDEX idx_municipios_geometrias_geom ON municipios_geometrias USING GIST(geom);
CREATE INDEX idx_municipios_geometrias_geom_simp ON municipios_geometrias USING GIST(geom_simplificada);
CREATE INDEX idx_municipios_geometrias_centroide ON municipios_geometrias USING GIST(centroide);

COMMENT ON TABLE municipios_geometrias IS 'Geometrias (shapefiles) dos 141 municípios MT';
COMMENT ON COLUMN municipios_geometrias.geom IS 'Geometria original SIRGAS 2000 → WGS84 (ST_Transform)';
COMMENT ON COLUMN municipios_geometrias.geom_simplificada IS 'ST_Simplify(geom, 0.001) para performance em zoom baixo';
COMMENT ON COLUMN municipios_geometrias.centroide IS 'ST_Centroid(geom) para labels no mapa';

-- =========================================================================
-- 3. Tabela de classificação LIRAa (Levantamento Rápido Aedes aegypti)
-- =========================================================================

CREATE TABLE IF NOT EXISTS liraa_classificacao (
    id SERIAL PRIMARY KEY,
    codigo_ibge VARCHAR(7) REFERENCES municipios_ibge(codigo_ibge),
    municipio_nome VARCHAR(100) NOT NULL,  -- Nome original do CSV (para auditoria)
    ano INTEGER NOT NULL,
    ciclo VARCHAR(20) NOT NULL,  -- Ex: "Jan/2025"
    classificacao VARCHAR(10) NOT NULL CHECK (classificacao IN ('Alerta', 'Risco', 'Satisfatório')),
    fonte VARCHAR(200),  -- Ex: "SES-MT Alerta 001/2025"
    observacoes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE (codigo_ibge, ano, ciclo)  -- Um município tem apenas 1 classificação por ciclo
);

CREATE INDEX idx_liraa_codigo_ibge ON liraa_classificacao(codigo_ibge);
CREATE INDEX idx_liraa_classificacao ON liraa_classificacao(classificacao);
CREATE INDEX idx_liraa_ano_ciclo ON liraa_classificacao(ano, ciclo);

COMMENT ON TABLE liraa_classificacao IS 'Classificação de risco LIRAa (SES-MT) por município e ciclo';
COMMENT ON COLUMN liraa_classificacao.classificacao IS 'Alerta (risco alto), Risco (risco médio), Satisfatório (baixo risco)';
COMMENT ON COLUMN liraa_classificacao.municipio_nome IS 'Nome original do CSV antes do fuzzy match';

-- =========================================================================
-- 4. Tabela de casos SINAN (notificações dengue por semana epidemiológica)
-- =========================================================================

-- Criar hypertable TimescaleDB se não existir
CREATE TABLE IF NOT EXISTS casos_sinan (
    id BIGSERIAL,
    codigo_ibge VARCHAR(7) NOT NULL REFERENCES municipios_ibge(codigo_ibge),
    data_semana DATE NOT NULL,  -- Data de início da semana epidemiológica
    ano INTEGER NOT NULL,
    semana_epidemiologica INTEGER NOT NULL CHECK (semana_epidemiologica BETWEEN 1 AND 53),
    numero_casos INTEGER NOT NULL CHECK (numero_casos >= 0),
    fonte VARCHAR(50) DEFAULT 'SINAN',  -- 'SINAN', 'SIGES-MT', etc.
    arquivo_origem VARCHAR(200),  -- Ex: "DENGBR25-MT.prn"
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    PRIMARY KEY (data_semana, codigo_ibge)  -- Particiona por data
);

-- Converter para hypertable TimescaleDB (se extensão estiver instalada)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM pg_extension WHERE extname = 'timescaledb'
    ) THEN
        PERFORM create_hypertable('casos_sinan', 'data_semana', if_not_exists => TRUE);
        
        -- Criar políticas de retenção (opcional): manter apenas últimos 5 anos
        -- PERFORM add_retention_policy('casos_sinan', INTERVAL '5 years', if_not_exists => TRUE);
    END IF;
END$$;

-- Índices
CREATE INDEX idx_casos_sinan_codigo_ibge ON casos_sinan(codigo_ibge, data_semana DESC);
CREATE INDEX idx_casos_sinan_ano ON casos_sinan(ano, semana_epidemiologica);
CREATE INDEX idx_casos_sinan_created ON casos_sinan(created_at DESC);

COMMENT ON TABLE casos_sinan IS 'Notificações de dengue SINAN por município e semana epidemiológica (hypertable TimescaleDB)';
COMMENT ON COLUMN casos_sinan.data_semana IS 'Data de início da semana epidemiológica (calculada a partir do ano + semana)';
COMMENT ON COLUMN casos_sinan.semana_epidemiologica IS 'Semana epidemiológica (1-53)';

-- =========================================================================
-- 5. View: Municípios com dados consolidados
-- =========================================================================

CREATE OR REPLACE VIEW v_municipios_completo AS
SELECT 
    mi.codigo_ibge,
    mi.nome,
    mi.populacao_estimada_2025,
    mi.area_km2,
    mi.idhm_2010,
    mi.pib_per_capita_2021,
    mg.geom,
    mg.geom_simplificada,
    mg.centroide,
    lc.classificacao AS liraa_classificacao,
    lc.ciclo AS liraa_ciclo,
    COALESCE(cs.total_casos_2025, 0) AS total_casos_2025,
    CASE 
        WHEN mi.populacao_estimada_2025 > 0 THEN 
            ROUND((COALESCE(cs.total_casos_2025, 0)::NUMERIC / mi.populacao_estimada_2025) * 100000, 2)
        ELSE 0
    END AS incidencia_2025  -- Casos por 100.000 habitantes
FROM municipios_ibge mi
LEFT JOIN municipios_geometrias mg ON mi.codigo_ibge = mg.codigo_ibge
LEFT JOIN (
    SELECT DISTINCT ON (codigo_ibge) 
        codigo_ibge, classificacao, ciclo
    FROM liraa_classificacao
    ORDER BY codigo_ibge, ano DESC, id DESC
) lc ON mi.codigo_ibge = lc.codigo_ibge
LEFT JOIN (
    SELECT 
        codigo_ibge,
        SUM(numero_casos) AS total_casos_2025
    FROM casos_sinan
    WHERE ano = 2025
    GROUP BY codigo_ibge
) cs ON mi.codigo_ibge = cs.codigo_ibge;

COMMENT ON VIEW v_municipios_completo IS 'View consolidada: IBGE + geometrias + LIRAa + casos SINAN 2025';

-- =========================================================================
-- 6. Função auxiliar: Calcular data da semana epidemiológica
-- =========================================================================

CREATE OR REPLACE FUNCTION calcular_data_semana_epi(p_ano INTEGER, p_semana INTEGER)
RETURNS DATE AS $$
DECLARE
    v_data_base DATE;
    v_data_semana DATE;
BEGIN
    -- Data base: primeiro dia do ano
    v_data_base := make_date(p_ano, 1, 1);
    
    -- Ajustar para o domingo mais próximo (início da semana epidemiológica)
    -- Semana epidemiológica inicia no domingo
    v_data_base := v_data_base - CAST(EXTRACT(DOW FROM v_data_base) AS INTEGER);
    
    -- Adicionar (semana - 1) * 7 dias
    v_data_semana := v_data_base + ((p_semana - 1) * 7);
    
    RETURN v_data_semana;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

COMMENT ON FUNCTION calcular_data_semana_epi IS 'Converte ano + semana epidemiológica em DATE (início da semana)';

-- Exemplo de uso:
-- SELECT calcular_data_semana_epi(2025, 1);  -- Retorna: 2024-12-29 (início da semana 1 de 2025)

-- =========================================================================
-- 7. Trigger: Atualizar updated_at automaticamente
-- =========================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_municipios_ibge_updated_at
    BEFORE UPDATE ON municipios_ibge
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_municipios_geometrias_updated_at
    BEFORE UPDATE ON municipios_geometrias
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_liraa_classificacao_updated_at
    BEFORE UPDATE ON liraa_classificacao
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =========================================================================
-- 8. Dados iniciais: Placeholder (dados reais carregados via script Python)
-- =========================================================================

-- Comentário: A carga real de dados será feita via script Python:
--   1. backend/scripts/import_dados_mt.py (IBGE, shapefiles, LIRAa)
--   2. backend/epi-api/app/services/etl_sinan.py (SINAN .prn)

-- =========================================================================
-- FIM DA MIGRAÇÃO V012
-- =========================================================================

-- Verificação final
DO $$
BEGIN
    RAISE NOTICE '✅ Migração V012 aplicada com sucesso!';
    RAISE NOTICE '   - Tabelas criadas: municipios_ibge, municipios_geometrias, liraa_classificacao, casos_sinan';
    RAISE NOTICE '   - View criada: v_municipios_completo';
    RAISE NOTICE '   - Função criada: calcular_data_semana_epi()';
    RAISE NOTICE '   - Próximo passo: executar backend/scripts/import_dados_mt.py';
END$$;
