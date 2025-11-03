#!/usr/bin/env python3
"""
Testar parser SINAN (.prn) - Validar estrutura e parsing

Execução:
  python backend/scripts/test_parser_sinan.py

Objetivo:
  - Validar leitura do arquivo DENGBR25-MT.prn
  - Extrair código IBGE + nome município
  - Parsear 42 semanas epidemiológicas
  - Calcular data de cada semana
  - Validar 141 municípios
"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import sys

# =========================================================================
# Configuração
# =========================================================================

BASE_DIR = Path(__file__).parent.parent.parent
SINAN_FILE = BASE_DIR / 'dados-mt' / 'SINAN' / 'DENGBR25-MT.prn'

# =========================================================================
# Funções
# =========================================================================

def calcular_data_semana_epi(ano: int, semana: int) -> str:
    """
    Calcular data de início da semana epidemiológica
    
    Semana epidemiológica: inicia no domingo
    Semana 1: primeiro domingo do ano (ou último de dezembro anterior)
    
    Args:
        ano: Ano (ex: 2025)
        semana: Semana epidemiológica (1-53)
    
    Returns:
        Data no formato YYYY-MM-DD
    """
    # Primeiro dia do ano
    data_base = datetime(ano, 1, 1)
    
    # Ajustar para o domingo mais próximo (início da semana epidemiológica)
    # weekday(): 0=Monday, 6=Sunday
    dias_para_domingo = (6 - data_base.weekday()) % 7
    if dias_para_domingo > 3:  # Se está muito longe, voltar para domingo anterior
        dias_para_domingo -= 7
    
    data_semana_1 = data_base + timedelta(days=dias_para_domingo)
    
    # Adicionar (semana - 1) semanas
    data_semana_n = data_semana_1 + timedelta(weeks=(semana - 1))
    
    return data_semana_n.strftime('%Y-%m-%d')

def parse_sinan_prn(file_path: Path, ano: int) -> pd.DataFrame:
    """
    Parsear arquivo SINAN .prn
    
    Formato:
      "510010 Acorizal",2,0,1,1,1,0,0,0,1,0,0,1,1,0,0,0,0,0,1,1,5,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,18
    
    Colunas:
      1: "Código IBGE + Nome" (ex: "510010 Acorizal")
      2-43: Semanas 01-42
      44: Total
    
    Returns:
        DataFrame com colunas: codigo_ibge, nome_municipio, semana, casos, data_semana
    """
    print(f"\n📁 Lendo arquivo: {file_path.name}")
    
    # Ler CSV (tentar diferentes encodings)
    encodings = ['utf-8', 'latin1', 'windows-1252', 'iso-8859-1']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(file_path, encoding=enc)
            print(f"  ✅ Encoding detectado: {enc}")
            break
        except UnicodeDecodeError:
            continue
    
    if df is None:
        raise ValueError(f"Não foi possível ler o arquivo com encodings: {encodings}")
    
    print(f"  📋 Linhas: {len(df)}")
    print(f"  📋 Colunas: {len(df.columns)}")
    
    # Primeira coluna: "Mun US Noti MT" (código IBGE + nome)
    # Colunas 2-43: "Semana 01", "Semana 02", ..., "Semana 42"
    # Coluna 44: "Total"
    
    # Validar estrutura
    if len(df.columns) < 44:
        raise ValueError(f"Arquivo com menos de 44 colunas: {len(df.columns)}")
    
    coluna_municipio = df.columns[0]
    colunas_semanas = [col for col in df.columns if 'Semana' in col]
    
    print(f"  ✅ Coluna município: '{coluna_municipio}'")
    print(f"  ✅ Colunas semanas: {len(colunas_semanas)}")
    
    # Extrair dados
    registros = []
    municipios_ok = 0
    municipios_erro = 0
    
    for idx, row in df.iterrows():
        # Extrair código IBGE e nome
        mun_col = str(row[coluna_municipio])
        
        # Formato: "510010 Acorizal" ou "5100102 Acorizal"
        partes = mun_col.split(' ', 1)
        if len(partes) != 2:
            municipios_erro += 1
            print(f"  ⚠️  Linha {idx+2}: formato inválido '{mun_col}'")
            continue
        
        codigo_ibge = partes[0].strip()
        nome_municipio = partes[1].strip()
        
        # Validar código IBGE (6 ou 7 dígitos, prefixo 51)
        if not codigo_ibge.isdigit() or not codigo_ibge.startswith('51'):
            municipios_erro += 1
            print(f"  ⚠️  Linha {idx+2}: código IBGE inválido '{codigo_ibge}'")
            continue
        
        # Se código tem 6 dígitos, adicionar dígito verificador (ex: 510010 → 5100102)
        if len(codigo_ibge) == 6:
            # Não temos algoritmo do dígito verificador, usar tabela IBGE
            # Por ora, apenas avisar
            pass
        
        municipios_ok += 1
        
        # Extrair casos por semana
        for semana in range(1, 43):  # Semanas 1-42
            col_name = f"Semana {semana:02d}"
            if col_name not in df.columns:
                continue
            
            n_casos = int(row[col_name]) if pd.notna(row[col_name]) else 0
            
            # Calcular data da semana
            data_semana = calcular_data_semana_epi(ano, semana)
            
            registros.append({
                'codigo_ibge': codigo_ibge,
                'nome_municipio': nome_municipio,
                'ano': ano,
                'semana_epidemiologica': semana,
                'numero_casos': n_casos,
                'data_semana': data_semana,
                'arquivo_origem': file_path.name
            })
    
    print(f"\n  ✅ Municípios OK: {municipios_ok}")
    print(f"  ⚠️  Municípios com erro: {municipios_erro}")
    print(f"  📊 Registros gerados: {len(registros)} (semanas × municípios)")
    
    # Criar DataFrame
    df_resultado = pd.DataFrame(registros)
    
    return df_resultado

def validar_dados(df: pd.DataFrame):
    """Validar consistência dos dados parseados"""
    print(f"\n🔍 VALIDAÇÃO DOS DADOS")
    print("="*70)
    
    # 1. Número de municípios únicos
    municipios_unicos = df['codigo_ibge'].nunique()
    print(f"  📊 Municípios únicos: {municipios_unicos}")
    if municipios_unicos == 141:
        print(f"     ✅ Correto! (141 municípios MT)")
    else:
        print(f"     ⚠️  Esperado: 141, encontrado: {municipios_unicos}")
    
    # 2. Número de semanas por município
    semanas_por_mun = df.groupby('codigo_ibge')['semana_epidemiologica'].nunique()
    semanas_media = semanas_por_mun.mean()
    print(f"\n  📊 Semanas por município: {semanas_media:.1f} (média)")
    if semanas_media == 42:
        print(f"     ✅ Correto! (42 semanas)")
    else:
        print(f"     ⚠️  Esperado: 42, encontrado: {semanas_media:.1f}")
    
    # 3. Total de casos
    total_casos = df['numero_casos'].sum()
    print(f"\n  📊 Total de casos (2025): {total_casos:,}")
    
    # 4. Top 5 municípios com mais casos
    top_5 = df.groupby(['codigo_ibge', 'nome_municipio'])['numero_casos'].sum().sort_values(ascending=False).head(5)
    print(f"\n  📊 Top 5 municípios com mais casos:")
    for (codigo, nome), casos in top_5.items():
        print(f"     {codigo} {nome:<30} {casos:>6,} casos")
    
    # 5. Validar códigos IBGE
    codigos_invalidos = df[~df['codigo_ibge'].str.match(r'^51\d{5}$')]
    if len(codigos_invalidos) > 0:
        print(f"\n  ⚠️  {len(codigos_invalidos)} registros com código IBGE inválido:")
        print(codigos_invalidos[['codigo_ibge', 'nome_municipio']].drop_duplicates().head(10))
    else:
        print(f"\n  ✅ Todos os códigos IBGE são válidos (51XXXXX)")
    
    # 6. Validar datas
    data_min = df['data_semana'].min()
    data_max = df['data_semana'].max()
    print(f"\n  📅 Período:")
    print(f"     Início: {data_min}")
    print(f"     Fim:    {data_max}")
    
    # 7. Amostra de dados
    print(f"\n  📋 Amostra de dados (5 primeiros registros):")
    print(df.head(5)[['codigo_ibge', 'nome_municipio', 'semana_epidemiologica', 'numero_casos', 'data_semana']].to_string(index=False))
    
    print("\n" + "="*70)

# =========================================================================
# Main
# =========================================================================

def main():
    print("\n")
    print("="*70)
    print(" 🧪 TESTE PARSER SINAN (.prn)")
    print("="*70)
    print(f"  Arquivo: {SINAN_FILE}")
    print("="*70)
    
    if not SINAN_FILE.exists():
        print(f"\n❌ Arquivo não encontrado: {SINAN_FILE}")
        return 1
    
    try:
        # Parsear arquivo
        df = parse_sinan_prn(SINAN_FILE, ano=2025)
        
        # Validar dados
        validar_dados(df)
        
        # Salvar amostra em CSV
        output_file = BASE_DIR / 'backend' / 'scripts' / 'sinan_parsed_sample.csv'
        df.head(1000).to_csv(output_file, index=False, encoding='utf-8')
        print(f"\n💾 Amostra salva em: {output_file.name} (1000 primeiros registros)")
        
        print("\n" + "="*70)
        print("✅ TESTE CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print("\n📊 Próximos passos:")
        print("  1. Criar endpoint: POST /api/etl/sinan/import")
        print("  2. Implementar service: backend/epi-api/app/services/etl_sinan.py")
        print("  3. Testar importação completa (3 anos: 2023, 2024, 2025)")
        print("\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Erro ao parsear arquivo: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
