-- Transferir geometrias da tabela temp_shapefile_mt para municipios_geometrias
INSERT INTO municipios_geometrias (
    codigo_ibge,
    geom,
    geom_simplificada,
    centroide,
    area_calculada_km2,
    perimetro_km
)
SELECT
    cd_mun AS codigo_ibge,
    geom,
    ST_Simplify(geom, 0.001) AS geom_simplificada,
    ST_Centroid(geom) AS centroide,
    ROUND(ST_Area(geom::geography) / 1000000, 3) AS area_calculada_km2,
    ROUND(ST_Perimeter(geom::geography) / 1000, 2) AS perimetro_km
FROM temp_shapefile_mt
WHERE cd_mun IS NOT NULL
ON CONFLICT (codigo_ibge) DO UPDATE SET
    geom = EXCLUDED.geom,
    geom_simplificada = EXCLUDED.geom_simplificada,
    centroide = EXCLUDED.centroide,
    area_calculada_km2 = EXCLUDED.area_calculada_km2,
    updated_at = NOW();

DROP TABLE IF EXISTS temp_shapefile_mt;
