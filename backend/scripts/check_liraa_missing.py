#!/usr/bin/env python3
"""
Verifica quais municípios do arquivo LIRAa não foram importados.
"""
import os
import csv
import psycopg2
from pathlib import Path

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'techdengue'),
    'user': os.getenv('POSTGRES_USER', 'techdengue'),
    'password': os.getenv('POSTGRES_PASSWORD', 'techdengue')
}

BASE_DIR = Path(__file__).parent.parent.parent
LIRAA_FILE = BASE_DIR / 'dados-mt' / 'LIRAa_MT_2025_-_Ciclo_Janeiro__classifica__o_.csv'

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Pegar nomes importados
    cur.execute("SELECT DISTINCT municipio_nome FROM liraa_classificacao")
    importados = {row[0].lower().strip() for row in cur.fetchall()}
    
    # Pegar nomes do IBGE
    cur.execute("SELECT codigo_ibge, nome FROM municipios_ibge")
    ibge_nomes = {row[1].lower().strip(): row[0] for row in cur.fetchall()}
    
    conn.close()
    
    # Ler arquivo LIRAa
    with open(LIRAA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        liraa_nomes = [row['municipio'].strip() for row in reader]
    
    print(f"\n{'='*70}")
    print(" 🔍 ANÁLISE LIRAa - Municípios Não Importados")
    print(f"{'='*70}")
    print(f"Total no arquivo LIRAa: {len(liraa_nomes)}")
    print(f"Total importados: {len(importados)}")
    print(f"Total no IBGE: {len(ibge_nomes)}")
    print(f"\n{'='*70}")
    print(" Municípios NÃO importados (precisam mapeamento manual):")
    print(f"{'='*70}\n")
    
    missing = []
    for nome in liraa_nomes:
        nome_lower = nome.lower().strip()
        if nome_lower not in importados:
            # Tentar encontrar similar no IBGE
            similar = None
            for ibge_nome in ibge_nomes.keys():
                if nome_lower in ibge_nome or ibge_nome in nome_lower:
                    similar = ibge_nome
                    break
            
            missing.append({
                'liraa': nome,
                'similar': similar,
                'codigo': ibge_nomes.get(similar) if similar else None
            })
    
    for i, m in enumerate(missing, 1):
        print(f"{i:3d}. '{m['liraa']}'")
        if m['similar']:
            print(f"      → Similar IBGE: '{m['similar']}' ({m['codigo']})")
        else:
            print(f"      → Sem match óbvio")
        print()
    
    print(f"{'='*70}")
    print(f" Total a mapear: {len(missing)}")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
