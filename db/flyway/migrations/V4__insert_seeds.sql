-- Minimal seeds
INSERT INTO indicador_epi (competencia, municipio_cod_ibge, indicador, valor)
VALUES (date_trunc('month', now())::date, '5103403', 'incidencia_100k', 0.0)
ON CONFLICT DO NOTHING;
