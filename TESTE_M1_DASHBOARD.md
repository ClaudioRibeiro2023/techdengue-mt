# 🧪 GUIA DE TESTES - M1 Dashboard & API

**Data**: 2025-11-03  
**Objetivo**: Validar integração completa Frontend ↔ API

---

## 🎯 PRÉ-REQUISITOS

### 1. Backend API Rodando
```powershell
# Verificar se containers estão UP
docker compose -f infra\docker-compose.yml ps

# Esperado:
# infra-db-1         Up (5432)
# infra-epi-api-1    Up (8000)
```

### 2. Testar Health da API
```bash
curl http://localhost:8000/api/health
```

**Resposta esperada**:
```json
{"status":"ok","service":"epi-api","version":"1.0.0"}
```

---

## ✅ TESTE 1: Endpoints da API

### 1.1 Estatísticas 2025
```bash
curl "http://localhost:8000/api/mapa/estatisticas?ano=2025&semana_epi_inicio=1&semana_epi_fim=42"
```

**Validar**:
- ✅ `total_casos`: 34276
- ✅ `total_municipios`: 141
- ✅ `incidencia_media`: ~1194.27
- ✅ `distribuicao_risco`: {"BAIXO":7,"MEDIO":22,"ALTO":19,"MUITO_ALTO":93}

### 1.2 Série Temporal Cuiabá
```bash
curl "http://localhost:8000/api/mapa/series-temporais/5103403?ano=2025"
```

**Validar**:
- ✅ `codigo_ibge`: "5103403"
- ✅ `nome`: "Cuiabá"
- ✅ `serie`: array com 42 objetos
- ✅ Cada objeto tem `data` (ex: "2025-W01") e `valor` (incidência)

### 1.3 Heatmap
```bash
curl "http://localhost:8000/api/mapa/heatmap?ano=2025&semana_epi_inicio=1&semana_epi_fim=42"
```

**Validar**:
- ✅ `points`: array com 141 objetos
- ✅ Cada ponto tem `lat`, `lng`, `intensity`
- ✅ `max_intensity`: ~10594.12
- ✅ `total_points`: 141

---

## ✅ TESTE 2: Frontend Dashboard

### 2.1 Instalar Dependências
```bash
cd frontend
npm install
```

### 2.2 Configurar Proxy (se necessário)
Editar `frontend/vite.config.ts`:

```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      }
    }
  }
})
```

### 2.3 Rodar Frontend
```bash
npm run dev
```

**Esperado**:
```
VITE v5.x.x ready in XXX ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### 2.4 Acessar Dashboard
Abrir no browser: `http://localhost:5173/dashboard-epi`

---

## ✅ TESTE 3: Validação Visual no Browser

### 3.1 KPI Cards

**Verificar se exibem**:
1. **Total de Casos**: ~34.276 casos
   - Ícone azul (Activity)
   - Descrição: "141 municípios afetados"

2. **Total de Óbitos**: 0 óbitos
   - Ícone vermelho (AlertCircle)

3. **Taxa de Letalidade**: 0,0%
   - Ícone laranja (AlertTriangle)

4. **Incidência Média**: ~1.194,27 /100k hab
   - Ícone amarelo (TrendingUp)
   - Descrição: "Máxima: 10594.12/100k"

5. **Municípios Alto Risco**: 112 municípios
   - Ícone vermelho (Users)

### 3.2 Gráfico de Série Temporal

**Verificar**:
- ✅ Título: "Evolução Temporal"
- ✅ Subtítulo: "Cuiabá"
- ✅ Eixo X: Semanas (2025-W01 até 2025-W42)
- ✅ Eixo Y: Incidência /100k hab
- ✅ Linha azul conectando pontos
- ✅ Pico visível na semana 2

### 3.3 Gráfico Top 10

**Verificar**:
- ✅ Título: "Top 10 Municípios"
- ✅ Barra horizontal ou vertical
- ✅ 10 municípios ordenados por incidência
- ✅ Cores diferentes por nível de risco

### 3.4 Filtros

**Testar interatividade**:
- ✅ Dropdown Ano: 2025, 2024, 2023
- ✅ Input Semana Início: 1-53
- ✅ Input Semana Fim: 1-53
- ✅ Dropdown Doença: Todas, Dengue, etc.
- ✅ Ao mudar filtros, dados recarregam

### 3.5 Console do Browser

**Verificar ausência de erros**:
- ✅ Sem erros de CORS
- ✅ Sem erros 404
- ✅ Sem erros de TypeScript
- ✅ Chamadas HTTP 200 OK

**Abrir DevTools (F12) → Network**:
```
GET /api/mapa/estatisticas?ano=2025... → 200 OK
GET /api/mapa/series-temporais/5103403?ano=2025 → 200 OK
GET /api/mapa/heatmap?ano=2025... → 200 OK
```

---

## ✅ TESTE 4: Performance

### 4.1 Tempo de Carregamento
- ✅ Carregamento inicial: < 3s
- ✅ Resposta API estatísticas: < 2s
- ✅ Resposta API série temporal: < 1s
- ✅ Resposta API heatmap: < 2s

### 4.2 Uso de Memória
- ✅ Frontend: < 100 MB
- ✅ API: < 500 MB
- ✅ PostgreSQL: estável

---

## 🐛 TROUBLESHOOTING

### Problema 1: CORS Error
**Erro**: `Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS`

**Solução**:
1. Adicionar proxy no `vite.config.ts` (ver seção 2.2)
2. OU configurar CORS na API (`epi-api/app/main.py`)

### Problema 2: API não responde
**Erro**: `Failed to fetch` ou timeout

**Solução**:
```bash
# Reiniciar API
docker compose -f infra\docker-compose.yml restart epi-api

# Ver logs
docker logs infra-epi-api-1 --tail 100
```

### Problema 3: Dados não carregam
**Erro**: Loading infinito ou erro de dados

**Solução**:
1. Verificar se banco tem dados:
```powershell
.\validate_m1_db.ps1
```

2. Verificar formato de resposta no Network tab
3. Confirmar que transformação de dados está correta no `DashboardEPI.tsx`

### Problema 4: Gráficos não aparecem
**Erro**: Componente vazio ou erro de renderização

**Solução**:
1. Verificar se biblioteca de gráficos está instalada:
```bash
npm list recharts
npm list chart.js
```

2. Verificar estrutura de dados no console:
```javascript
console.log('Series data:', series);
console.log('TopN data:', topN);
```

---

## 📊 RESULTADOS ESPERADOS

### Dashboard Funcional ✅
- [x] 5 KPIs exibindo dados reais
- [x] Série temporal Cuiabá (42 pontos)
- [x] Top 10 municípios por incidência
- [x] Filtros interativos funcionando
- [x] Sem erros no console
- [x] Performance < 3s carregamento

### API Funcional ✅
- [x] Health check OK
- [x] Estatísticas retornando 34.276 casos
- [x] Série temporal 42 semanas
- [x] Heatmap 141 pontos
- [x] Tempo de resposta < 2s

---

## 📸 SCREENSHOTS ESPERADOS

### 1. Dashboard Principal
```
┌─────────────────────────────────────────────────┐
│  Dashboard Epidemiológico                       │
│  Indicadores e métricas - MT                    │
├─────────────────────────────────────────────────┤
│  [Ano: 2025] [Semana: 1] [Fim: 42] [Dengue]   │
├──────────┬──────────┬──────────┬──────────┬────┤
│ 34.276   │    0     │   0,0%   │ 1194,27  │ 112│
│ casos    │ óbitos   │letalidade│ /100k    │mun │
├──────────┴──────────┴──────────┴──────────┴────┤
│  Evolução Temporal          │ Top 10 Municípios│
│  [Gráfico Linha Cuiabá]     │ [Gráfico Barras] │
│                              │                  │
└──────────────────────────────┴──────────────────┘
```

---

## ✅ CHECKLIST FINAL DE TESTES

**Backend**:
- [ ] Docker compose UP
- [ ] API health OK
- [ ] Estatísticas retornam 34.276
- [ ] Série temporal 42 pontos
- [ ] Heatmap 141 pontos

**Frontend**:
- [ ] npm install sem erros
- [ ] npm run dev inicia
- [ ] Dashboard abre no browser
- [ ] 5 KPIs exibem dados
- [ ] Gráfico série temporal aparece
- [ ] Gráfico top 10 aparece
- [ ] Filtros funcionam
- [ ] Console sem erros
- [ ] Network requests 200 OK

**Performance**:
- [ ] Carregamento < 3s
- [ ] APIs respondem < 2s
- [ ] Sem memory leaks

---

## 🎯 PRÓXIMOS PASSOS (Após Testes)

1. **Se tudo OK** ✅:
   - Documentar screenshots
   - Criar release notes
   - Preparar deploy

2. **Se houver problemas** ⚠️:
   - Anotar erros específicos
   - Ver logs detalhados
   - Ajustar conforme troubleshooting

3. **Melhorias futuras** 💡:
   - Adicionar mais municípios na série
   - Implementar cache Redis
   - Adicionar testes E2E
   - Integrar relatórios PDF

---

**📋 EXECUTE ESTE GUIA PASSO A PASSO**  
**⏱️ Tempo estimado: 15-20 minutos**  
**🎯 Meta: Dashboard funcionando 100%**

Última atualização: 2025-11-03 00:30 UTC-3
