#!/usr/bin/env python3
"""
Importar arquivos SINAN agregados (.prn) com semanas epidemiológicas para a tabela casos_sinan.

Formato esperado (exemplo - DENGBR25-MT.prn):
"Mun US Noti MT","Semana 01",...,"Semana 42","Total"
"510010 Acorizal",2,0,...,18

- Extrai código (6 dígitos) e nome do município da primeira coluna
- Mapeia para código IBGE de 7 dígitos usando municipios_ibge
- Para cada semana N com valor > 0:
  - Calcula data_semana via função calcular_data_semana_epi(ano, N)
  - Insere/atualiza em casos_sinan (PK: data_semana, codigo_ibge)

Execução:
  python backend/scripts/import_sinan_prn.py
"""

import csv
import os
import re
from pathlib import Path
from typing import Dict, Tuple

import psycopg2
from psycopg2.extras import execute_batch

DB_CONFIG = {
    'host': os.getenv('POSTGRES_HOST', 'localhost'),
    'port': int(os.getenv('POSTGRES_PORT', 5432)),
    'database': os.getenv('POSTGRES_DB', 'techdengue'),
    'user': os.getenv('POSTGRES_USER', 'techdengue'),
    'password': os.getenv('POSTGRES_PASSWORD', 'techdengue')
}

BASE_DIR = Path(__file__).parent.parent.parent
SINAN_DIR = BASE_DIR / 'dados-mt' / 'SINAN'

COD6_RE = re.compile(r'^"?(\d{6})\s+(.+?)"?$')


def get_db():
    return psycopg2.connect(**DB_CONFIG)


def map_cod6_to_cod7(cur, cod6: str, nome: str) -> Tuple[str, bool]:
    """Mapeia código de 6 dígitos do PRN para IBGE 7 dígitos usando prefixo e/ou nome.
    Retorna (codigo_ibge_7, via_nome)
    """
    # Tentativa por prefixo
    cur.execute("SELECT codigo_ibge FROM municipios_ibge WHERE codigo_ibge LIKE %s LIMIT 2", (cod6 + '%',))
    rows = cur.fetchall()
    if len(rows) == 1:
        return rows[0][0], False

    # Tentativa por nome (case-insensitive)
    cur.execute("SELECT codigo_ibge FROM municipios_ibge WHERE LOWER(nome) = LOWER(%s) LIMIT 1", (nome.strip(),))
    row = cur.fetchone()
    if row:
        return row[0], True

    # Fallback: primeira opção por prefixo
    return (rows[0][0], False) if rows else (None, False)


def year_from_filename(filename: str) -> int:
    # Padrão DENGBRYY-MT.prn (YY = 23,24,25)
    m = re.search(r'DENGBR(\d{2})', filename.upper())
    if not m:
        return 0
    yy = int(m.group(1))
    return 2000 + yy


def import_file(conn, prn_path: Path) -> Dict[str, int]:
    print(f"\n📄 Importando {prn_path.name}")
    year = year_from_filename(prn_path.name)
    if year == 0:
        print("  ❌ Não foi possível inferir o ano a partir do nome do arquivo")
        return {"processed": 0, "inserted": 0, "updated": 0}

    # Detectar encoding
    encodings = ['utf-8', 'latin-1']
    reader = None
    last_exc = None
    for enc in encodings:
        try:
            f = prn_path.open('r', encoding=enc)
            reader = csv.reader(f)
            header = next(reader)
            break
        except Exception as e:
            last_exc = e
    if reader is None:
        print(f"  ❌ Falha ao abrir arquivo: {last_exc}")
        return {"processed": 0, "inserted": 0, "updated": 0}

    # Identificar colunas semana
    week_cols = []
    for idx, col in enumerate(header):
        col_norm = col.strip().strip('"').lower()
        if col_norm.startswith('semana '):
            try:
                w = int(col_norm.split('semana ')[1])
                week_cols.append((idx, w))
            except Exception:
                pass
    if not week_cols:
        print("  ❌ Nenhuma coluna 'Semana N' encontrada no header")
        return {"processed": 0, "inserted": 0, "updated": 0}

    cur = conn.cursor()

    insert_sql = (
        """
        INSERT INTO casos_sinan (
            codigo_ibge, data_semana, ano, semana_epidemiologica, numero_casos, fonte, arquivo_origem
        )
        VALUES (%s, calcular_data_semana_epi(%s, %s), %s, %s, %s, 'SINAN', %s)
        ON CONFLICT (data_semana, codigo_ibge)
        DO UPDATE SET numero_casos = EXCLUDED.numero_casos, arquivo_origem = EXCLUDED.arquivo_origem
        """
    )

    processed = inserted = updated = 0

    batch_params = []

    for row in reader:
        if not row:
            continue
        first = row[0].strip()
        m = COD6_RE.match(first)
        if not m:
            # pular header ou linhas inválidas
            continue
        cod6, nome = m.group(1), m.group(2)
        cod7, via_nome = map_cod6_to_cod7(cur, cod6, nome)
        if not cod7:
            print(f"  ⚠️  Não foi possível mapear código {cod6} ({nome}) para IBGE 7 dígitos")
            continue

        # Para cada coluna de semana, coletar valor
        for col_idx, semana in week_cols:
            try:
                val = row[col_idx].strip()
                casos = int(val) if val != '' else 0
            except Exception:
                casos = 0
            if casos < 0:
                casos = 0
            # Adicionar ao batch
            batch_params.append((cod7, year, semana, year, semana, casos, prn_path.name))
            processed += 1

    if batch_params:
        try:
            execute_batch(cur, insert_sql, batch_params, page_size=1000)
            conn.commit()
            # Não é trivially distinguir inserted vs updated aqui sem triggers; marcar como processed
        except Exception as e:
            conn.rollback()
            print(f"  ❌ Erro ao inserir batch: {e}")
            return {"processed": processed, "inserted": 0, "updated": 0}

    print(f"  ✅ Registros processados: {processed}")
    return {"processed": processed, "inserted": 0, "updated": 0}


def main():
    print("\n" + "="*70)
    print(" 🧪 IMPORTAÇÃO SINAN (.prn) → casos_sinan")
    print("="*70)
    print(f"  Diretório: {SINAN_DIR}")

    if not SINAN_DIR.exists():
        print(f"❌ Diretório não encontrado: {SINAN_DIR}")
        return 1

    files = sorted([p for p in SINAN_DIR.glob('DENGBR*-MT.prn')])
    if not files:
        print("❌ Nenhum arquivo DENGBR*-MT.prn encontrado")
        return 1

    conn = get_db()
    total_processed = 0
    for p in files:
        stats = import_file(conn, p)
        total_processed += stats.get('processed', 0)

    conn.close()

    print("\n" + "="*70)
    print(f" ✅ FIM. Total linhas semana processadas: {total_processed}")
    print("="*70)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
