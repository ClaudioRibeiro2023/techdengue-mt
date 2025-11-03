#!/usr/bin/env python3
"""
Validar shapefiles MT - Projeção e Atributos
"""
import struct
import sys
from pathlib import Path

def read_dbf_header(dbf_path: Path):
    """Ler cabeçalho do arquivo DBF"""
    with open(dbf_path, 'rb') as f:
        # Ler cabeçalho DBF (32 bytes)
        header = f.read(32)
        
        # Número de registros (bytes 4-7, little-endian)
        num_records = struct.unpack('<I', header[4:8])[0]
        
        # Tamanho do cabeçalho (bytes 8-9, little-endian)
        header_size = struct.unpack('<H', header[8:10])[0]
        
        # Tamanho de cada registro (bytes 10-11, little-endian)
        record_size = struct.unpack('<H', header[10:12])[0]
        
        print(f"📊 DBF Header Info:")
        print(f"  - Registros: {num_records}")
        print(f"  - Tamanho cabeçalho: {header_size} bytes")
        print(f"  - Tamanho registro: {record_size} bytes")
        print()
        
        # Ler descritores de campos (32 bytes cada)
        num_fields = (header_size - 33) // 32  # -33 para remover cabeçalho + terminador
        fields = []
        
        for i in range(num_fields):
            field_desc = f.read(32)
            if len(field_desc) < 32:
                break
                
            # Nome do campo (11 bytes, null-terminated)
            name = field_desc[0:11].split(b'\x00')[0].decode('utf-8', errors='ignore')
            
            # Tipo do campo (1 byte)
            field_type = chr(field_desc[11])
            
            # Tamanho do campo (1 byte)
            field_length = field_desc[16]
            
            fields.append({
                'name': name,
                'type': field_type,
                'length': field_length
            })
        
        print(f"📋 Campos DBF ({len(fields)} colunas):")
        for field in fields:
            type_name = {
                'C': 'Character',
                'N': 'Numeric',
                'F': 'Float',
                'L': 'Logical',
                'D': 'Date'
            }.get(field['type'], field['type'])
            print(f"  - {field['name']:<15} ({type_name}, {field['length']})")
        
        return num_records, fields

def validate_projection(prj_path: Path):
    """Validar arquivo de projeção"""
    with open(prj_path, 'r') as f:
        prj_content = f.read()
    
    print(f"🗺️  Projeção:")
    if 'SIRGAS_2000' in prj_content or 'SIRGAS 2000' in prj_content:
        print(f"  ✅ SIRGAS 2000 (EPSG:4674)")
        print(f"  ⚠️  Nota: Leaflet usa WGS84 (EPSG:4326)")
        print(f"  💡 Solução: usar ST_Transform(geom, 4326) no PostGIS")
        return 'SIRGAS_2000'
    elif 'WGS_1984' in prj_content or 'WGS 84' in prj_content:
        print(f"  ✅ WGS84 (EPSG:4326) - compatível direto")
        return 'WGS84'
    else:
        print(f"  ❌ Projeção desconhecida")
        print(f"  Conteúdo: {prj_content[:100]}...")
        return 'UNKNOWN'

def main():
    base_path = Path(__file__).parent.parent.parent / 'dados-mt' / 'IBGE' / 'MT_Municipios_2024_shp_limites'
    
    prj_file = base_path / 'MT_Municipios_2024.prj'
    dbf_file = base_path / 'MT_Municipios_2024.dbf'
    shp_file = base_path / 'MT_Municipios_2024.shp'
    
    print("=" * 70)
    print("VALIDAÇÃO SHAPEFILES MT 2024")
    print("=" * 70)
    print()
    
    # Validar existência dos arquivos
    print("📁 Arquivos:")
    for f in [shp_file, dbf_file, prj_file]:
        exists = "✅" if f.exists() else "❌"
        size = f"{f.stat().st_size / 1024 / 1024:.2f} MB" if f.exists() else "N/A"
        print(f"  {exists} {f.name:<30} {size:>10}")
    print()
    
    # Validar projeção
    if prj_file.exists():
        projection = validate_projection(prj_file)
        print()
    
    # Validar DBF
    if dbf_file.exists():
        num_records, fields = read_dbf_header(dbf_file)
        print()
        
        # Verificar se tem código IBGE
        has_ibge = any('CD_MUN' in f['name'].upper() or 'IBGE' in f['name'].upper() or 'GEOCOD' in f['name'].upper() for f in fields)
        has_nome = any('NM_MUN' in f['name'].upper() or 'NOME' in f['name'].upper() for f in fields)
        
        print("🔍 Validação:")
        print(f"  - Número de municípios: {num_records}")
        print(f"  - Esperado (MT): 141")
        if num_records == 141:
            print(f"  ✅ Número correto!")
        else:
            print(f"  ⚠️  Diferença: {num_records - 141:+d}")
        
        print()
        if has_ibge:
            print(f"  ✅ Campo código IBGE encontrado")
        else:
            print(f"  ⚠️  Campo código IBGE NÃO encontrado")
            
        if has_nome:
            print(f"  ✅ Campo nome município encontrado")
        else:
            print(f"  ⚠️  Campo nome município NÃO encontrado")
    
    print()
    print("=" * 70)
    print("✅ Validação concluída")
    print("=" * 70)

if __name__ == '__main__':
    main()
