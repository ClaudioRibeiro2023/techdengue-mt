# Checklist de Validação - Árvore de Menus TechDengue

## 📊 Estrutura Completa (48 Funções)

### ✅ WEB MAPAS (1 módulo, 5 funções)
**Mapa Vivo** - `/mapa`
- [ ] Mapa Principal
- [ ] Mapa de Calor (?view=heatmap)
- [ ] Hotspots (?view=hotspots)
- [ ] Zonas de Risco (?view=risk)
- [ ] Camadas Externas (?view=layers)

### ✅ PAINÉIS (4 módulos, 15 funções)
**Panorama Executivo** - `/dashboard`
- [ ] Dashboard Consolidado
- [ ] Rankings (?view=rankings)
- [ ] Alertas (?view=alerts)
- [ ] Relatórios Rápidos (?view=reports)

**Relatórios & Indicadores** - `/relatorios`
- [ ] Relatórios EPI (?type=epi)
- [ ] Exportações (?view=export)
- [ ] Cadernos Analíticos (?view=notebooks)

**ETL & Integração** [BETA] - `/etl`
- [ ] Importadores (?view=importers)
- [ ] Tratamento/Mapeamento (?view=transform)
- [ ] Catálogo de Dados (?view=catalog)
- [ ] Qualidade & Rastros (?view=quality)

**Previsão & Simulação** [IA] - `/modulos/previsao-simulacao`
- [ ] Nowcasting / Rt (?view=nowcasting)
- [ ] Previsão 2-4 semanas (?view=forecast)
- [ ] Cenários de Intervenção (?view=scenarios)
- [ ] Risco Climático (?view=climate)

### ✅ VIGILÂNCIA (3 módulos, 15 funções)
**Vigilância Entomológica** - `/modulos/vigilancia-entomologica`
- [ ] Visão Geral (?view=overview)
- [ ] Análise Sazonal (?view=sazonal)
- [ ] Ovitrampas (?view=ovitrampas)
- [ ] Índices (IPO/IDO/IMO) (?view=indices)
- [ ] Qualidade (?view=qualidade)

**Vigilância Epidemiológica** - `/modulos/vigilancia-epidemiologica`
- [ ] Visão Geral (?view=overview)
- [ ] Séries Temporais (?view=temporal)
- [ ] Mapa de Incidência (?view=mapa)
- [ ] Hotspots (?view=hotspots)
- [ ] Qualidade (?view=qualidade)

**e-Denúncia** - `/denuncia`
- [ ] Nova Denúncia
- [ ] Consultar Protocolo (/:protocolo)
- [ ] Painel Operacional (?view=painel)
- [ ] Integração Atividades (?view=integration)
- [ ] Qualidade/Auditoria (?view=quality)

### ✅ OPERAÇÕES (1 módulo, 5 funções)
**Resposta Operacional** - `/modulos/resposta-operacional`
- [ ] Triagem & Despacho (?view=triagem)
- [ ] Planejamento de Campo (?view=planejamento)
- [ ] Execução (Mobile) (?view=execucao)
- [ ] Acompanhamento (?view=acompanhamento)
- [ ] Avaliação de Impacto (?view=impacto)

### ✅ SISTEMA (2 módulos, 8 funções)
**Administração** - `/modulos/administracao`
- [ ] Usuários e Perfis (?view=usuarios)
- [ ] Parâmetros do Sistema (?view=parametros)
- [ ] Entidades (?view=entidades)
- [ ] Auditoria & Logs (?view=audit)

**Observabilidade** [DEV] - `/modulos/observabilidade`
- [ ] Métricas (?view=metricas)
- [ ] Logs (?view=logs)
- [ ] Saúde (?view=health)
- [ ] Qualidade de Dados (?view=dataQuality)

---

## 🎯 Critérios de Validação

### Layout (3 Colunas)
- [ ] AppSidebar (dark) sempre visível
- [ ] FunctionsPanel (cards) sempre visível
- [ ] Conteúdo principal com header + card branco

### Visual
- [ ] Grupos separados por section headers
- [ ] Badges (BETA, IA, DEV) visíveis e estilizados
- [ ] Ícones corretos e proporcionais (16px sidebar, 20px cards)
- [ ] Active state com gradiente azul intenso
- [ ] Hover com transform e sombra

### Navegação
- [ ] Clicar em módulo (col 1) muda cards (col 2) e conteúdo (col 3)
- [ ] Clicar em card (col 2) ativa o card e muda URL (?view=...)
- [ ] Query params funcionam (testar ?view=heatmap, etc)
- [ ] Fallback: home (/) mostra painel do Mapa Vivo por padrão

### Categorias
- [ ] ANALISE (15 funções)
- [ ] OPERACIONAL (13 funções)
- [ ] CONTROLE (12 funções)
- [ ] MAPEAMENTO (5 funções)
- [ ] INDICADORES (3 funções)

---

## 📈 Estatísticas
- **Total:** 11 módulos, 48 funções
- **Grupos:** 5 (Web Mapas, Painéis, Vigilância, Operações, Sistema)
- **Badges:** 3 (BETA, IA, DEV)
- **Query params:** 39 views dinâmicas
- **Ícones:** 48 (Lucide)

---

## ⚠️ Problemas Conhecidos
- [ ] Páginas ainda são placeholders (mostram "Em Desenvolvimento")
- [ ] Rotas com `:protocolo` não funcionam (placeholder)
- [ ] Service Worker (PWA) pode cachear recursos antigos

---

## 🔄 Refresh Recomendado
Se algo não refletir:
1. Hard refresh: Ctrl+Shift+R
2. DevTools → Application → Service Workers → Unregister → Reload
3. Limpar cache do navegador
