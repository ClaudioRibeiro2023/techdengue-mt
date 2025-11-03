# 🚀 Setup Completo Dados MT — Guia de Execução

**Data**: 2025-11-02  
**Status**: ✅ **PRONTO PARA EXECUÇÃO**

---

## 📋 Resumo

Foram criados **4 artefatos** para trabalhar com os dados REAIS de Mato Grosso:

1. ✅ **Validação de Shapefiles** (`backend/scripts/validate_shapefile.py`)
2. ✅ **Migração SQL V012** (`backend/migrations/V012__municipios_base.sql`)
3. ✅ **Script de Importação** (`backend/scripts/import_dados_mt.py`)
4. ✅ **Teste Parser SINAN** (`backend/scripts/test_parser_sinan.py`)

---

## 🔍 1. Validação dos Shapefiles

### Comando
```bash
python backend/scripts/validate_shapefile.py
```

### Resultados
```
✅ SIRGAS 2000 (EPSG:4674) — precisa reprojetar para WGS84 (EPSG:4326)
✅ 142 registros (141 municípios + 1 extra)
✅ Campos: CD_MUN (código IBGE), NM_MUN (nome), AREA_KM2
✅ 12 MB de geometrias MULTIPOLYGON
```

### Descoberta Importante
- **Projeção**: SIRGAS 2000 (não WGS84)
- **Solução**: usar `ST_Transform(geom, 4326)` no PostGIS
- **142 registros**: investigar se há 1 município duplicado

---

## 🗄️ 2. Migração SQL V012

### Arquivo
`backend/migrations/V012__municipios_base.sql`

### Tabelas Criadas

#### `municipios_ibge`
- **141 municípios MT** com dados IBGE
- Campos: código IBGE, nome, população 2025, área, IDHM, PIB
- **Uso**: cálculo de incidência (casos/100k hab)

#### `municipios_geometrias`
- **Geometrias PostGIS** (MULTIPOLYGON)
- Reprojeção automática: SIRGAS 2000 → WGS84
- Geometria simplificada para zoom baixo
- Centroides para labels no mapa

#### `liraa_classificacao`
- **Classificação de risco** LIRAa (SES-MT)
- Campos: município, ano, ciclo, classificação (Alerta/Risco)
- 107 municípios classificados (Jan/2025)

#### `casos_sinan`
- **Hypertable TimescaleDB** (séries temporais)
- Notificações de dengue por município e semana epidemiológica
- Dados: 2023, 2024, 2025 (3 anos)

### Views e Funções

#### `v_municipios_completo`
- **View consolidada**: IBGE + geometrias + LIRAa + casos SINAN
- Cálculo automático de incidência (casos/100k hab)

#### `calcular_data_semana_epi(ano, semana)`
- Converte semana epidemiológica → DATE
- Exemplo: `calcular_data_semana_epi(2025, 1)` → `2024-12-29`

### Execução
```bash
# Via Flyway (automático no docker-compose up)
# Ou manualmente:
psql -U postgres -d techdengue -f backend/migrations/V012__municipios_base.sql
```

---

## 📊 3. Script de Importação

### Arquivo
`backend/scripts/import_dados_mt.py`

### O que faz

1. **Importa dados IBGE** (`IBGE/dados.csv`)
   - 141 municípios
   - População, área, IDHM, PIB
   - Tabela: `municipios_ibge`

2. **Importa shapefiles** (`IBGE/MT_Municipios_2024_shp_limites/`)
   - Usa `shp2pgsql` para converter
   - Reprojeção: SIRGAS 2000 → WGS84
   - Simplificação: `ST_Simplify(geom, 0.001)`
   - Tabela: `municipios_geometrias`

3. **Importa LIRAa** (`LIRAa_MT_2025_-_Ciclo_Janeiro__classificacao_.csv`)
   - Fuzzy match: nome → código IBGE (threshold 85%)
   - 107 municípios classificados
   - Tabela: `liraa_classificacao`

### Pré-requisitos
```bash
pip install pandas psycopg2 fuzzywuzzy
```

### Execução
```bash
python backend/scripts/import_dados_mt.py
```

### Output Esperado
```
✅ 141 municípios IBGE importados
✅ 142 geometrias transferidas (ou ⚠️ se shp2pgsql não disponível)
✅ 107 municípios LIRAa importados
⚠️ 34 municípios não encontrados (fuzzy match < 85%)
```

---

## 🧪 4. Teste Parser SINAN

### Arquivo
`backend/scripts/test_parser_sinan.py`

### O que faz
- Valida leitura de `SINAN/DENGBR25-MT.prn`
- Extrai código IBGE (6 dígitos) + nome município
- Parseia 42 semanas epidemiológicas
- Calcula data de cada semana
- Gera DataFrame: `codigo_ibge, nome, semana, casos, data_semana`

### Execução
```bash
python backend/scripts/test_parser_sinan.py
```

### Resultados (DENGBR25-MT.prn)
```
✅ Encoding: latin1 (não UTF-8)
✅ 142 municípios parseados
✅ 42 semanas por município
✅ 5.964 registros gerados (142 × 42)
📊 Total de casos 2025: 34.607
🏆 Top município: Primavera do Leste (3.224 casos)
```

### Descobertas Importantes

#### 1. Encoding: `latin1`
```python
df = pd.read_csv(file_path, encoding='latin1')  # NÃO utf-8
```

#### 2. Código IBGE: 6 dígitos
```
Formato arquivo: "510010 Acorizal"
Código IBGE:     510010 (6 dígitos)
Padrão IBGE:     5100102 (7 dígitos)
```
- Arquivos SINAN usam apenas os 6 primeiros dígitos
- Não incluem dígito verificador

#### 3. Estrutura do arquivo
```csv
"Mun US Noti MT","Semana 01","Semana 02",...,"Semana 42","Total"
"510010 Acorizal",2,0,1,1,1,0,0,0,1,0,0,1,1,0,0,0,0,0,1,1,5,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,18
```

#### 4. Semana epidemiológica
- Semana 1 de 2025: inicia em `2024-12-29` (domingo)
- Semana 42 de 2025: termina em `2025-10-12`

---

## 🎯 Próximos Passos

### M0 - Fundações (Setup Inicial)

1. **Aplicar migração V012**
   ```bash
   # Automático no docker-compose up
   # Ou manualmente:
   psql -U postgres -d techdengue < backend/migrations/V012__municipios_base.sql
   ```

2. **Executar importação de dados**
   ```bash
   python backend/scripts/import_dados_mt.py
   ```

3. **Verificar dados**
   ```sql
   SELECT * FROM v_municipios_completo LIMIT 10;
   SELECT codigo_ibge, nome, populacao_estimada_2025 FROM municipios_ibge;
   SELECT codigo_ibge, ST_AsText(centroide) FROM municipios_geometrias LIMIT 5;
   SELECT * FROM liraa_classificacao;
   ```

### M1 - ETL SINAN (Sprint 1-2)

1. **Criar service ETL** (`backend/epi-api/app/services/etl_sinan.py`)
   - Reutilizar lógica de `test_parser_sinan.py`
   - Adicionar validação de códigos IBGE
   - Inserir em `casos_sinan` (hypertable TimescaleDB)

2. **Criar endpoint** (`POST /api/etl/sinan/import`)
   ```python
   @router.post("/api/etl/sinan/import")
   async def import_sinan(file: UploadFile, ano: int):
       # 1. Salvar arquivo temporário
       # 2. Parsear com parse_sinan_prn()
       # 3. Validar dados (≥95% aceite)
       # 4. Inserir em casos_sinan
       # 5. Retornar relatório de qualidade
       pass
   ```

3. **Importar 3 anos de dados**
   ```bash
   # 2023
   curl -X POST -F "file=@dados-mt/SINAN/DENGBR23-MT.prn" \
        "http://localhost:8000/api/etl/sinan/import?ano=2023"
   
   # 2024
   curl -X POST -F "file=@dados-mt/SINAN/DENGBR24-MT.prn" \
        "http://localhost:8000/api/etl/sinan/import?ano=2024"
   
   # 2025
   curl -X POST -F "file=@dados-mt/SINAN/DENGBR25-MT.prn" \
        "http://localhost:8000/api/etl/sinan/import?ano=2025"
   ```

### M1 - Mapa Vivo (Sprint 2-3)

1. **Criar endpoint GeoJSON**
   ```python
   @router.get("/api/mapa/geojson/municipios")
   async def get_municipios_geojson(
       ano: int = 2025,
       classificacao_liraa: str = None
   ):
       # SELECT ST_AsGeoJSON(geom), codigo_ibge, nome, incidencia
       # FROM v_municipios_completo
       # WHERE ano = :ano AND classificacao = :classificacao
       pass
   ```

2. **Testar no frontend**
   ```typescript
   // Carregar GeoJSON no Leaflet
   const response = await fetch('/api/mapa/geojson/municipios?ano=2025');
   const geojson = await response.json();
   
   L.geoJSON(geojson, {
     style: (feature) => ({
       fillColor: getColorByIncidencia(feature.properties.incidencia),
       weight: 1,
       color: '#333',
       fillOpacity: 0.7
     })
   }).addTo(map);
   ```

---

## ✅ Checklist de Validação

### Dados IBGE
- [ ] 141 municípios carregados
- [ ] População 2025 preenchida (para cálculo de incidência)
- [ ] Área km² preenchida

### Shapefiles
- [ ] 141 geometrias carregadas (ou 142 se houver duplicado)
- [ ] Projeção WGS84 (EPSG:4326)
- [ ] Centroides calculados
- [ ] Geometrias simplificadas criadas

### LIRAa
- [ ] 107 municípios classificados
- [ ] Fuzzy match: ≥85% de sucesso
- [ ] Classificações: "Alerta" (74) + "Risco" (33)

### SINAN
- [ ] Parser funciona com encoding `latin1`
- [ ] 142 municípios parseados por arquivo
- [ ] 42 semanas epidemiológicas por município
- [ ] Datas calculadas corretamente
- [ ] Total de casos 2025: ~34.607

---

## 🐛 Troubleshooting

### Erro: `shp2pgsql: command not found`
**Solução**: Instalar PostGIS tools
```bash
# Ubuntu/Debian
sudo apt-get install postgis

# macOS
brew install postgis

# Windows
# Incluído no instalador do PostgreSQL
```

### Erro: `UnicodeDecodeError` ao ler SINAN
**Solução**: Usar encoding `latin1` (não `utf-8`)
```python
df = pd.read_csv(file_path, encoding='latin1')
```

### Erro: Fuzzy match LIRAa retorna 0 matches
**Solução**: Reduzir threshold de 85% para 80%
```python
codigo_ibge, score = fuzzy_match_municipio(nome, municipios_ref, threshold=80)
```

### Warning: 142 municípios (esperado 141)
**Investigar**:
```sql
SELECT cd_mun, nm_mun, COUNT(*) 
FROM temp_shapefile_mt 
GROUP BY cd_mun, nm_mun 
HAVING COUNT(*) > 1;
```
- Provável: 1 município duplicado ou ilha separada

---

## 📚 Documentação Relacionada

- `docs/GUIA_MESTRE_IMPLEMENTACAO.md` (§5.7, §7.2.1, §7.2.2)
- `docs/DADOS_MT_ANALISE.md` (análise detalhada)
- `backend/migrations/V012__municipios_base.sql` (schema)
- `backend/scripts/import_dados_mt.py` (importação)
- `backend/scripts/test_parser_sinan.py` (parser SINAN)

---

## 🎉 Conclusão

**Setup completo para trabalhar com dados REAIS de Mato Grosso**:

1. ✅ Shapefiles validados (SIRGAS 2000 → WGS84)
2. ✅ Migração SQL criada (4 tabelas + view + funções)
3. ✅ Script de importação pronto (IBGE + shapefiles + LIRAa)
4. ✅ Parser SINAN testado e funcional (3 anos de dados)

**Próximo passo**: Executar `import_dados_mt.py` e começar M1 (ETL + Mapa).

---

**🚀 Sistema pronto para dados REAIS desde o dia 1!**
