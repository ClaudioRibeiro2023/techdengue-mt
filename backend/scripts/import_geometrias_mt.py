#!/usr/bin/env python3
"""
Importar geometrias dos municípios de MT a partir de shapefile (sem GDAL)

- Lê o shapefile com pyshp (pure Python)
- Constrói a geometria em GeoJSON e insere no PostGIS usando ST_GeomFromGeoJSON
- Reprojeta de SIRGAS 2000 (EPSG:4674) para WGS84 (EPSG:4326)

Execução:
  python backend/scripts/import_geometrias_mt.py
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, List

import shapefile  # pyshp
import psycopg2

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'techdengue'),
    'user': os.getenv('POSTGRES_USER', 'techdengue'),
    'password': os.getenv('POSTGRES_PASSWORD', 'techdengue')
}

BASE_DIR = Path(__file__).parent.parent.parent
SHP_PATH = BASE_DIR / 'dados-mt' / 'IBGE' / 'MT_Municipios_2024_shp_limites' / 'MT_Municipios_2024.shp'


def get_db_conn():
    return psycopg2.connect(**DB_CONFIG)


def find_code_field(reader: shapefile.Reader) -> Optional[str]:
    """Tenta identificar o campo do código IBGE no DBF."""
    # Campos existentes
    fields = [f[0] for f in reader.fields[1:]]  # pular DeletionFlag
    candidates: List[str] = [
        'CD_MUN', 'cd_mun', 'CD_GEOCMU', 'CD_GEOCODI', 'CD_GEOCOD', 'CD_GEOCODI', 'CD_GEOCMU_7', 'codigo_ibge', 'CODIGO_IBG'
    ]
    for c in candidates:
        if c in fields:
            return c
    # Fallback: se existir apenas um campo com 7 dígitos em várias linhas
    try:
        for f in fields:
            # verifique algumas amostras
            samples = [r.as_dict().get(f) for r in list(reader.iterShapeRecords())[:20]]
            if any(samples) and sum(1 for s in samples if s and len(str(s).strip()) == 7) >= 5:
                return f
    except Exception:
        pass
    return None


def shape_to_geojson_geometry(shape: shapefile.Shape) -> dict:
    """Converte um shapefile.Shape para um dict GeoJSON geometry.
    Usa __geo_interface__ se disponível (pyshp >= 2.x), senão reconstrói MultiPolygon das parts.
    """
    if hasattr(shape, '__geo_interface__'):
        gi = shape.__geo_interface__
        # Garantir que seja MultiPolygon
        if gi.get('type') == 'Polygon':
            return {'type': 'MultiPolygon', 'coordinates': [gi.get('coordinates', [])]}
        return gi

    # Fallback manual (Polygon/MultiPolygon)
    if shape.shapeType not in [shapefile.POLYGON, shapefile.POLYGONZ, shapefile.POLYGONM]:
        raise ValueError(f'ShapeType não suportado: {shape.shapeType}')

    parts_idx = list(shape.parts) + [len(shape.points)]
    rings = []
    for i in range(len(parts_idx) - 1):
        start, end = parts_idx[i], parts_idx[i+1]
        ring = shape.points[start:end]
        # Fechar anel se necessário
        if ring[0] != ring[-1]:
            ring = ring + [ring[0]]
        rings.append(ring)

    # Sem orientação de anel, tratar todos como polígonos externos
    multipolygon = [[rings[0]]]
    for ring in rings[1:]:
        multipolygon.append([ring])
    return {'type': 'MultiPolygon', 'coordinates': multipolygon}


def import_geometrias():
    print("\n" + "="*70)
    print("🗺️  IMPORTANDO GEOMETRIAS (shapefile → PostGIS)")
    print("="*70)
    print(f"  Shapefile: {SHP_PATH}")

    if not SHP_PATH.exists():
        print(f"❌ Shapefile não encontrado: {SHP_PATH}")
        return 1

    # Forçar encoding Latin-1 para evitar erros de decodificação do DBF
    reader = shapefile.Reader(str(SHP_PATH), encoding='latin-1')
    code_field = find_code_field(reader)
    if not code_field:
        print("❌ Campo de código IBGE não identificado no DBF")
        return 1

    print(f"  🔎 Campo de código IBGE: {code_field}")

    conn = get_db_conn()
    cur = conn.cursor()

    inserted = 0
    updated = 0

    for sr in reader.iterShapeRecords():
        props = sr.record.as_dict()
        codigo = str(props.get(code_field, '')).strip()
        if not codigo or len(codigo) < 7:
            continue
        codigo = codigo[:7]

        try:
            geom_geojson = shape_to_geojson_geometry(sr.shape)
            geom_json_str = json.dumps(geom_geojson)

            sql = """
            INSERT INTO municipios_geometrias (
                codigo_ibge, geom, geom_simplificada, centroide,
                area_calculada_km2, perimetro_km
            )
            SELECT
                %s,
                ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674), 4326) AS geom,
                ST_Simplify(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674), 4326), 0.001) AS geom_simplificada,
                ST_Centroid(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674), 4326)) AS centroide,
                (ST_Area(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674), 4326)::geography) / 1000000)::numeric(10,3) AS area_calculada_km2,
                (ST_Perimeter(ST_Transform(ST_SetSRID(ST_GeomFromGeoJSON(%s), 4674), 4326)::geography) / 1000)::numeric(10,2) AS perimetro_km
            ON CONFLICT (codigo_ibge) DO UPDATE SET
                geom = EXCLUDED.geom,
                geom_simplificada = EXCLUDED.geom_simplificada,
                centroide = EXCLUDED.centroide,
                area_calculada_km2 = EXCLUDED.area_calculada_km2,
                updated_at = NOW();
            """
            params = (
                codigo,
                geom_json_str, geom_json_str, geom_json_str, geom_json_str, geom_json_str
            )
            cur.execute(sql, params)
            if cur.rowcount == 1:
                inserted += 1
            else:
                updated += 1
        except Exception as e:
            print(f"  ⚠️  Falha para código {codigo}: {e}")
            conn.rollback()
            continue

    conn.commit()
    cur.close()
    conn.close()

    print(f"  ✅ Inseridos: {inserted} | Atualizados: {updated}")
    return 0


def main():
    try:
        return import_geometrias()
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
