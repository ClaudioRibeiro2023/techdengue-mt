#!/usr/bin/env python3
"""
Agrega casos_sinan (semanal) em indicador_epi para uso no Mapa/Dashboard.

- Agrupa por (codigo_ibge, ano, semana_epidemiologica)
- Define doenca_tipo = 'DENGUE'
- Preenche casos_confirmados com a soma de numero_casos
- UPSERT na PK composta (municipio_codigo, ano, semana_epi, doenca_tipo)

Execução:
  python backend/scripts/aggregate_sinan_to_indicador.py
"""
import os
import sys
import psycopg2

def main() -> int:
    cfg = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'database': os.getenv('POSTGRES_DB', 'techdengue'),
        'user': os.getenv('POSTGRES_USER', 'techdengue'),
        'password': os.getenv('POSTGRES_PASSWORD', 'techdengue')
    }
    try:
        conn = psycopg2.connect(**cfg)
        cur = conn.cursor()
        print("\n" + "="*70)
        print(" 🔄 Agregando casos_sinan → indicador_epi (DENGUE)")
        print("="*70)
        sql = """
        INSERT INTO indicador_epi (
            competencia, municipio_cod_ibge, indicador, valor
        )
        SELECT
            calcular_data_semana_epi(cs.ano, cs.semana_epidemiologica) AS competencia,
            cs.codigo_ibge AS municipio_cod_ibge,
            'CASOS_DENGUE'::text AS indicador,
            SUM(cs.numero_casos)::numeric AS valor
        FROM casos_sinan cs
        GROUP BY cs.codigo_ibge, cs.ano, cs.semana_epidemiologica;
        """
        cur.execute(sql)
        affected = cur.rowcount
        conn.commit()
        print(f" ✅ Upsert concluído (linhas afetadas: {affected})")
        return 0
    except Exception as e:
        print(f"❌ Erro: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
