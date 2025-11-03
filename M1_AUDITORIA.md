# M1 - AUDITORIA DE ESTADO ATUAL

**Data**: 2025-11-02 21:30  
**Objetivo**: Mapear o que existe vs GUIA_MESTRE_IMPLEMENTACAO.md §7.2 (M1)  
**Status M0**: ✅ 100% Completo (30/30 testes)

---

## RESUMO EXECUTIVO

### Estado Atual: M1 PARCIALMENTE IMPLEMENTADO

- **ETL SINAN/LIRAa**: ✅ 90% (backend pronto, falta integração final)
- **Mapa Vivo**: ⚠️ 60% (componentes React existem, falta integração API)
- **Dashboard EPI**: ⚠️ 50% (componentes existem, sem dados reais)
- **Relatório EPI01**: ❌ 0% (não iniciado)

---

## AUDITORIA DETALHADA

### ✅ 1. Dados MT (Base REAL)

**Localização**: `dados-mt/`

| Componente | Status | Arquivo | Tamanho |
|------------|--------|---------|---------|
| SINAN 2023 | ✅ Existe | `SINAN/DENGBR23-MT.prn` | ? |
| SINAN 2024 | ✅ Existe | `SINAN/DENGBR24-MT.prn` | ? |
| SINAN 2025 | ✅ Existe | `SINAN/DENGBR25-MT.prn` | ? |
| LIRAa 2025 | ✅ Existe | `LIRAa_MT_2025_-_Ciclo_Janeiro__classificacao_.csv` | ? |
| IBGE CSV | ✅ Existe | `IBGE/dados.csv` | ? |
| Shapefiles MT | ✅ Existe | `IBGE/MT_Municipios_2024_shp_limites/` | 12 MB |

**Scripts de Importação**:
- ✅ `backend/scripts/import_dados_mt.py` (14 KB)
- ✅ `backend/scripts/test_parser_sinan.py` (9.5 KB)
- ✅ `backend/scripts/validate_shapefile.py` (5 KB)

**Migração Database**:
- ✅ `backend/migrations/V012__municipios_base.sql` (11 KB)

### ⚠️ 2. ETL EPI (Backend epi-api)

**Routers** (`epi-api/app/routers/`):
- ✅ `etl.py` - Endpoints ETL
- ✅ `liraa.py` - LIRAa específico
- ✅ `mapa.py` - Camadas de mapa
- ✅ `dashboard.py` - KPIs

**Services** (`epi-api/app/services/`):
- ✅ `sinan_etl_service.py` - Parser SINAN
- ✅ `liraa_etl_service.py` - Parser LIRAa
- ✅ `etl_base_service.py` - Base comum
- ✅ `etl_validator.py` - Validações
- ✅ `etl_persistence.py` - Persistência DB
- ✅ `mapa_service.py` - Camadas mapa
- ✅ `dashboard_service.py` - KPIs

**Schemas** (`epi-api/app/schemas/`):
- ✅ `etl.py`, `etl_epi.py`
- ✅ `liraa.py`
- ✅ `mapa.py`
- ✅ `dashboard.py`

**Tasks Assíncronas** (`epi-api/app/tasks/`):
- ✅ `etl_tasks.py` - Celery tasks

**Testes**:
- ✅ `tests/test_etl.py`
- ✅ `tests/test_etl_endpoint.py`
- ✅ `tests/test_etl_validator.py`
- ✅ `tests/test_mapa.py`

**Status Backend**: ✅ **Estrutura completa**, precisa validar:
1. ❓ Endpoints estão funcionais?
2. ❓ Migração V012 foi aplicada no banco?
3. ❓ Dados MT foram importados?
4. ❓ Celery está configurado?

### ⚠️ 3. Mapa Vivo (Frontend)

**Componente Principal**:
- ✅ `frontend/src/pages/MapaVivo.tsx` (303 linhas)

**Estado do Componente**:
- ✅ Leaflet configurado
- ✅ 3 selects de filtro (Ano, Doença, Camada) com acessibilidade
- ✅ GeoJSON layer
- ✅ Heatmap (Circle markers)
- ✅ Legenda de risco
- ⚠️ **Tipagem**: FeatureCollection<Geometry, MunicipioProps>
- ⚠️ **Chamadas API**: Definidas mas não testadas com dados reais

**Filtros Implementados**:
- Ano: 2022, 2023, 2024
- Doença: Todas, DENGUE, ZIKA, CHIKUNGUNYA
- Camada: INCIDENCIA, IPO, IDO
- Semanas epidemiológicas (início/fim)

**Camadas Implementadas**:
- ✅ Base OSM (TileLayer)
- ✅ Choropleth (GeoJSON com style por nível_risco)
- ✅ Heatmap (Circle markers com intensidade)
- ❌ Hotspots (KDE) - não implementado
- ❌ LIRAa Risk Zones - não implementado

**APIs Esperadas** (conforme código):
- `GET /api/mapa/heatmap?...`
- `GET /api/mapa/camadas?...`

### ⚠️ 4. Dashboard EPI (Frontend)

**Componente Principal**:
- ✅ `frontend/src/pages/DashboardEPI.tsx` (280 linhas)

**Componentes Filhos**:
- ✅ `components/dashboard/KPICards.tsx` (125 linhas)
- ✅ `components/dashboard/TimeSeriesChart.tsx` (146 linhas)
- ✅ `components/dashboard/TopNChart.tsx` (180 linhas)

**Estado do Componente**:
- ✅ Tipagem completa (KpisData, TimeSeriesData, TopNData)
- ✅ 4 filtros (Ano, Semana Início, Semana Fim, Doença)
- ✅ 3 seções de dados (KPIs, Séries Temporais, Top N)
- ⚠️ **Chamadas API**: Definidas mas não testadas

**APIs Esperadas**:
- `GET /api/indicadores/kpis?...`
- `GET /api/indicadores/series-temporais?...`
- `GET /api/indicadores/top?...`

### ❌ 5. Relatório EPI01 (PDF/A-1)

**Status**: NÃO INICIADO

**Especificação (Guia §7.2.3)**:
- Formato: PDF/A-1 + CSV
- Geração: Assíncrona (< 30s)
- Hash: SHA-256 no rodapé
- Gráficos: Matplotlib embarcados

**Falta criar**:
- `relatorios-api/app/routers/epi01.py`
- `relatorios-api/app/services/epi01_service.py`
- `relatorios-api/app/schemas/epi01.py`
- Frontend: botão "Gerar EPI01" no Dashboard

### ⚠️ 6. Observability M1

**Já existe (M0)**:
- ✅ Health endpoints
- ✅ Métricas Prometheus
- ✅ X-Request-ID
- ✅ Logs JSON estruturados

**Falta adicionar (M1)**:
- ❌ SLOs específicos de M1:
  - ETL: p95 ≤ 2s/1k linhas
  - Mapa: p95 ≤ 4s/10k features
  - Dashboard: p95 ≤ 500ms
  - EPI01: ≤ 30s
- ❌ Alertas específicos (5xx > 2%, p95 > targets)

---

## PRÓXIMOS PASSOS CRÍTICOS

### Etapa 1: Validar Infraestrutura (30 min)

1. **Verificar se V012 foi aplicada**:
   ```bash
   docker exec -it infra-db-1 psql -U techdengue -d techdengue -c "\dt"
   # Procurar: municipios_ibge, municipios_geometrias, liraa_classificacao, casos_sinan
   ```

2. **Se V012 não foi aplicada**, aplicar:
   ```bash
   # Copiar V012__municipios_base.sql para infra/flyway/migrations/
   # Reiniciar container DB
   ```

3. **Executar importação de dados MT**:
   ```bash
   cd backend/scripts
   python import_dados_mt.py
   ```

4. **Validar dados importados**:
   ```sql
   SELECT COUNT(*) FROM municipios_ibge;  -- Espera: 141
   SELECT COUNT(*) FROM liraa_classificacao;  -- Espera: 107
   SELECT COUNT(*) FROM casos_sinan;  -- Espera: ~6k (142 municípios × 42 semanas)
   ```

### Etapa 2: Testar Endpoints epi-api (1h)

1. **Iniciar epi-api** (se não estiver rodando):
   ```bash
   cd infra && docker compose up -d epi-api
   ```

2. **Testar endpoints ETL**:
   ```bash
   # Health
   curl http://localhost:8000/api/health
   
   # Listar cargas ETL
   curl http://localhost:8000/api/etl/status
   
   # Importar SINAN (via endpoint)
   # Importar LIRAa (via endpoint)
   ```

3. **Testar endpoints Mapa**:
   ```bash
   # GeoJSON municípios
   curl "http://localhost:8000/api/mapa/camadas?ano=2025&tipo_camada=INCIDENCIA"
   
   # Heatmap
   curl "http://localhost:8000/api/mapa/heatmap?ano=2025"
   ```

4. **Testar endpoints Dashboard**:
   ```bash
   # KPIs
   curl "http://localhost:8000/api/indicadores/kpis?ano=2025"
   
   # Séries temporais
   curl "http://localhost:8000/api/indicadores/series-temporais?ano=2025"
   
   # Top N
   curl "http://localhost:8000/api/indicadores/top?ano=2025&limite=10"
   ```

### Etapa 3: Integrar Frontend com Backend (2h)

1. **Atualizar variáveis de ambiente frontend** (.env):
   ```bash
   VITE_API_URL=http://localhost:8000/api
   ```

2. **Testar MapaVivo.tsx** no navegador:
   - Abrir http://localhost:5173/mapa
   - Verificar se GeoJSON carrega
   - Verificar se heatmap aparece
   - Testar filtros

3. **Testar DashboardEPI.tsx**:
   - Abrir http://localhost:5173/dashboard
   - Verificar se KPIs carregam
   - Verificar gráficos

### Etapa 4: Implementar EPI01 (3-4h)

**Pendente** - vem depois das etapas 1-3.

---

## CRITÉRIOS DE ACEITE M1 (Guia §7.2)

- [ ] ETL processa 1k linhas < 5s
- [ ] Mapa 141 municípios < 3s
- [ ] Dashboard KPIs corretos
- [ ] EPI01 PDF hash válido
- [ ] 5 camadas de mapa funcionais
- [ ] Performance p95 dentro dos SLOs

---

## DECISÃO: INICIAR VALIDAÇÃO OU IMPLEMENTAÇÃO?

### Opção A: Validar o que existe (Recomendado)
1. Aplicar V012 (se não aplicada)
2. Importar dados MT
3. Testar todos endpoints existentes
4. Documentar gaps específicos
5. Implementar apenas o que falta

### Opção B: Reimplementar do zero
- ❌ Desperdício: já há 90% do backend
- ❌ Risco: perder código validado

**RECOMENDAÇÃO**: **OPÇÃO A** - Validar primeiro, implementar gaps depois.

---

## COMANDOS DE VALIDAÇÃO RÁPIDA

```bash
# 1. Verificar serviços rodando
cd infra && docker compose ps

# 2. Verificar se V012 existe no banco
docker exec -it infra-db-1 psql -U techdengue -d techdengue -c "\dt municipios*"

# 3. Testar epi-api
curl http://localhost:8000/api/health
curl http://localhost:8000/api/etl/status

# 4. Testar frontend
cd frontend && npm run dev
# Abrir http://localhost:5173
```

---

**PRÓXIMA AÇÃO RECOMENDADA**: Executar Etapa 1 (Validar Infraestrutura).

Aguardo sua confirmação para prosseguir. ⏸️
