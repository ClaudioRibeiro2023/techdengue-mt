#!/usr/bin/env python3
"""
Importar dados MT (IBGE, shapefiles, LIRAa) para PostgreSQL/PostGIS

Execução:
  python backend/scripts/import_dados_mt.py

Pré-requisitos:
  - PostgreSQL/PostGIS rodando (docker-compose up)
  - Migração V012 aplicada
  - Bibliotecas: pandas, psycopg2, fuzzywuzzy
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import subprocess
import sys
import os
from typing import List, Dict, Tuple
from fuzzywuzzy import fuzz

# =========================================================================
# Configuração
# =========================================================================

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'techdengue'),
    'user': os.getenv('POSTGRES_USER', 'postgres'),
    'password': os.getenv('POSTGRES_PASSWORD', 'postgres')
}

BASE_DIR = Path(__file__).parent.parent.parent
DADOS_DIR = BASE_DIR / 'dados-mt'

# =========================================================================
# Utilitários
# =========================================================================

def get_db_connection():
    """Criar conexão com PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def limpar_texto(texto: str) -> str:
    """Normalizar texto (remover acentos, lowercase)"""
    import unicodedata
    if not texto:
        return ""
    texto = str(texto)
    texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('ASCII')
    return texto.lower().strip()

def fuzzy_match_municipio(nome_original: str, municipios_ref: List[Dict], threshold: int = 85) -> Tuple[str, int]:
    """
    Fuzzy match de nome de município
    
    Args:
        nome_original: Nome do município a buscar
        municipios_ref: Lista de dicts com {'codigo_ibge', 'nome'}
        threshold: Score mínimo para aceitar (0-100)
    
    Returns:
        (codigo_ibge, score) ou (None, 0) se não encontrar
    """
    nome_normalizado = limpar_texto(nome_original)
    
    best_match = None
    best_score = 0
    
    for mun in municipios_ref:
        nome_ref = limpar_texto(mun['nome'])
        score = fuzz.ratio(nome_normalizado, nome_ref)
        
        if score > best_score:
            best_score = score
            best_match = mun['codigo_ibge']
    
    if best_score >= threshold:
        return best_match, best_score
    else:
        return None, best_score

# =========================================================================
# 1. Importar dados IBGE
# =========================================================================

def import_ibge_data(conn):
    """Importar dados IBGE (população, área, IDHM, PIB)"""
    print("\n" + "="*70)
    print("📊 IMPORTANDO DADOS IBGE")
    print("="*70)
    
    csv_path = DADOS_DIR / 'IBGE' / 'dados.csv'
    
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return False
    
    # Ler CSV (primeira linha é header descritivo, segunda é header real)
    df = pd.read_csv(csv_path, skiprows=1, encoding='utf-8')
    
    # Renomear colunas para match com tabela
    df.columns = [col.split('[')[0].strip() for col in df.columns]
    
    print(f"  📁 Arquivo: {csv_path.name}")
    print(f"  📋 Linhas: {len(df)}")
    print(f"  📋 Colunas: {len(df.columns)}")
    
    # Preparar dados
    registros = []
    for _, row in df.iterrows():
        codigo = str(row.get('Código', '')).strip()
        if not codigo or len(codigo) != 7:
            continue
        
        # Converter valores numéricos (tratar '-' como NULL)
        def parse_num(val, tipo=float):
            if pd.isna(val) or str(val).strip() in ['-', '']:
                return None
            try:
                return tipo(str(val).replace(',', '.'))
            except:
                return None
        
        registro = (
            codigo,  # codigo_ibge
            str(row.get('Município', '')).strip(),  # nome
            str(row.get('Gentílico', '')).strip() or None,  # gentilico
            str(row.get('Prefeito', '')).strip() or None,  # prefeito_2025
            parse_num(row.get('Área Territorial - km²'), float),  # area_km2
            parse_num(row.get('População no último censo - pessoas'), int),  # populacao_censo_2022
            parse_num(row.get('Densidade demográfica - hab/km²'), float),  # densidade_demografica
            parse_num(row.get('População estimada - pessoas'), int),  # populacao_estimada_2025
            parse_num(row.get('Escolarização 6 a 14 anos - %'), float),  # escolarizacao_6_14
            parse_num(row.get('IDHM Índice de desenvolvimento humano municipal'), float),  # idhm_2010
            parse_num(row.get('Mortalidade infantil - óbitos por mil nascidos vivos'), float),  # mortalidade_infantil_2023
            parse_num(row.get('Total de receitas brutas realizadas - R$'), float),  # receitas_brutas_2024
            parse_num(row.get('Total de despesas brutas empenhadas - R$'), float),  # despesas_brutas_2024
            parse_num(row.get('PIB per capita - R$'), float)  # pib_per_capita_2021
        )
        registros.append(registro)
    
    # Inserir no banco
    cursor = conn.cursor()
    
    sql = """
    INSERT INTO municipios_ibge (
        codigo_ibge, nome, gentilico, prefeito_2025, area_km2,
        populacao_censo_2022, densidade_demografica, populacao_estimada_2025,
        escolarizacao_6_14, idhm_2010, mortalidade_infantil_2023,
        receitas_brutas_2024, despesas_brutas_2024, pib_per_capita_2021
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (codigo_ibge) DO UPDATE SET
        nome = EXCLUDED.nome,
        populacao_estimada_2025 = EXCLUDED.populacao_estimada_2025,
        updated_at = NOW()
    """
    
    execute_batch(cursor, sql, registros, page_size=100)
    conn.commit()
    
    print(f"  ✅ {len(registros)} municípios IBGE importados")
    
    return True

# =========================================================================
# 2. Importar shapefiles (PostGIS)
# =========================================================================

def import_shapefiles(conn):
    """Importar shapefiles MT usando shp2pgsql"""
    print("\n" + "="*70)
    print("🗺️  IMPORTANDO SHAPEFILES MT")
    print("="*70)
    
    shp_path = DADOS_DIR / 'IBGE' / 'MT_Municipios_2024_shp_limites' / 'MT_Municipios_2024.shp'
    
    if not shp_path.exists():
        print(f"❌ Arquivo não encontrado: {shp_path}")
        return False
    
    # Criar tabela temporária para importação
    temp_table = 'temp_shapefile_mt'
    
    # Comando shp2pgsql
    # -I: criar índice espacial
    # -s 4674:4326: converter de SIRGAS 2000 (4674) para WGS84 (4326)
    # -d: drop table se existir
    # -W UTF-8: encoding
    
    cmd = [
        'shp2pgsql',
        '-I',  # Criar índice espacial
        '-s', '4674:4326',  # Reprojetar de SIRGAS 2000 para WGS84
        '-d',  # Drop table se existir
        '-W', 'UTF-8',  # Encoding
        str(shp_path),
        f'public.{temp_table}'
    ]
    
    print(f"  📁 Shapefile: {shp_path.name}")
    print(f"  🔄 Convertendo SIRGAS 2000 → WGS84...")
    
    try:
        # Executar shp2pgsql e pegar output SQL
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        sql_output = result.stdout
        
        # Executar SQL no banco
        cursor = conn.cursor()
        cursor.execute(sql_output)
        conn.commit()
        
        print(f"  ✅ Shapefile importado na tabela temporária '{temp_table}'")
        
        # Transferir dados para municipios_geometrias
        print(f"  🔄 Transferindo para 'municipios_geometrias'...")
        
        sql_transfer = f"""
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
            ST_Simplify(geom, 0.001) AS geom_simplificada,  -- Simplificar para zoom baixo
            ST_Centroid(geom) AS centroide,
            ROUND(ST_Area(geom::geography) / 1000000, 3) AS area_calculada_km2,  -- m² → km²
            ROUND(ST_Perimeter(geom::geography) / 1000, 2) AS perimetro_km  -- m → km
        FROM {temp_table}
        WHERE cd_mun IS NOT NULL
        ON CONFLICT (codigo_ibge) DO UPDATE SET
            geom = EXCLUDED.geom,
            geom_simplificada = EXCLUDED.geom_simplificada,
            centroide = EXCLUDED.centroide,
            area_calculada_km2 = EXCLUDED.area_calculada_km2,
            updated_at = NOW()
        """
        
        cursor.execute(sql_transfer)
        rows_inserted = cursor.rowcount
        conn.commit()
        
        print(f"  ✅ {rows_inserted} geometrias transferidas")
        
        # Limpar tabela temporária
        cursor.execute(f"DROP TABLE IF EXISTS {temp_table}")
        conn.commit()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"  ❌ Erro ao executar shp2pgsql:")
        print(f"     {e.stderr}")
        return False
    except Exception as e:
        print(f"  ❌ Erro ao importar shapefile: {e}")
        return False

# =========================================================================
# 3. Importar classificação LIRAa
# =========================================================================

def import_liraa(conn):
    """Importar classificação LIRAa (CSV)"""
    print("\n" + "="*70)
    print("🦟 IMPORTANDO CLASSIFICAÇÃO LIRAa")
    print("="*70)
    
    csv_path = DADOS_DIR / 'LIRAa_MT_2025_-_Ciclo_Janeiro__classificacao_.csv'
    
    if not csv_path.exists():
        print(f"❌ Arquivo não encontrado: {csv_path}")
        return False
    
    # Ler CSV
    df = pd.read_csv(csv_path, encoding='utf-8')
    
    print(f"  📁 Arquivo: {csv_path.name}")
    print(f"  📋 Linhas: {len(df)}")
    
    # Buscar municípios IBGE para fuzzy match
    cursor = conn.cursor()
    cursor.execute("SELECT codigo_ibge, nome FROM municipios_ibge")
    municipios_ref = [{'codigo_ibge': row[0], 'nome': row[1]} for row in cursor.fetchall()]
    
    print(f"  🔍 Referência: {len(municipios_ref)} municípios IBGE")
    
    # Processar cada linha
    registros = []
    matches_ok = 0
    matches_fail = 0
    
    for _, row in df.iterrows():
        nome_original = str(row.get('municipio', '')).strip()
        classificacao = str(row.get('classificacao', '')).strip()
        ano = int(row.get('ano', 2025))
        ciclo = str(row.get('ciclo', '')).strip()
        fonte = str(row.get('fonte', '')).strip()
        
        if not nome_original or not classificacao:
            continue
        
        # Fuzzy match
        codigo_ibge, score = fuzzy_match_municipio(nome_original, municipios_ref, threshold=85)
        
        if codigo_ibge:
            matches_ok += 1
            registros.append((
                codigo_ibge,
                nome_original,
                ano,
                ciclo,
                classificacao,
                fonte
            ))
        else:
            matches_fail += 1
            print(f"  ⚠️  Município não encontrado: '{nome_original}' (score: {score}%)")
    
    # Inserir no banco
    sql = """
    INSERT INTO liraa_classificacao (
        codigo_ibge, municipio_nome, ano, ciclo, classificacao, fonte
    ) VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (codigo_ibge, ano, ciclo) DO UPDATE SET
        classificacao = EXCLUDED.classificacao,
        fonte = EXCLUDED.fonte,
        updated_at = NOW()
    """
    
    execute_batch(cursor, sql, registros, page_size=100)
    conn.commit()
    
    print(f"  ✅ {matches_ok} municípios LIRAa importados")
    print(f"  ⚠️  {matches_fail} municípios não encontrados (fuzzy match < 85%)")
    
    return True

# =========================================================================
# Main
# =========================================================================

def main():
    print("\n")
    print("="*70)
    print(" 🚀 IMPORTAÇÃO DE DADOS MT")
    print("="*70)
    print(f"  Base de dados: {DADOS_DIR}")
    print(f"  PostgreSQL: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    print("="*70)
    
    try:
        # Conectar ao banco
        conn = get_db_connection()
        print("\n✅ Conexão PostgreSQL estabelecida")
        
        # 1. Importar dados IBGE
        if not import_ibge_data(conn):
            print("\n❌ Falha ao importar dados IBGE")
            return 1
        
        # 2. Importar shapefiles
        if not import_shapefiles(conn):
            print("\n⚠️  Falha ao importar shapefiles (prosseguindo...)")
            # Não retornar erro, pois shp2pgsql pode não estar disponível
        
        # 3. Importar LIRAa
        if not import_liraa(conn):
            print("\n❌ Falha ao importar LIRAa")
            return 1
        
        # Fechar conexão
        conn.close()
        
        # Resumo final
        print("\n" + "="*70)
        print("✅ IMPORTAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print("\n📊 Próximos passos:")
        print("  1. Verificar dados: SELECT * FROM v_municipios_completo LIMIT 10;")
        print("  2. Importar SINAN: python backend/scripts/import_sinan.py")
        print("  3. Testar API Mapa: GET /api/mapa/geojson/municipios")
        print("\n")
        
        return 0
        
    except psycopg2.Error as e:
        print(f"\n❌ Erro PostgreSQL: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
