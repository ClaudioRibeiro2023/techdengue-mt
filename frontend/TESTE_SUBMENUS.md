# 🧪 TESTE EXAUSTIVO - SUBMENUS COM SUBTÍTULOS

## 📋 Checklist de Validação

Execute os testes abaixo e marque ✅ após validação.

---

## 1️⃣ PREVISÃO & SIMULAÇÃO

### **Acesso**: `/modulos/previsao-simulacao`

### **Functions Esperadas** (4 total):

#### ✅ ANALISE (4 funções)

1. **Nowcasting / Rt**
   - Subtitle: "Atraso de notificação e transmissibilidade"
   - Icon: Zap ⚡
   - Path: `?view=nowcasting`
   - [ ] Subtitle visível e correto?
   - [ ] Ícone renderizado?
   - [ ] Link funcional?

2. **Previsão 2–4 semanas**
   - Subtitle: "Casos/risco por município"
   - Icon: TrendingUp 📈
   - Path: `?view=forecast`
   - [ ] Subtitle visível e correto?
   - [ ] Ícone renderizado?
   - [ ] Link funcional?

3. **Cenários de Intervenção**
   - Subtitle: "Simulação de impacto"
   - Icon: GitBranch 🌿
   - Path: `?view=scenarios`
   - [ ] Subtitle visível e correto?
   - [ ] Ícone renderizado?
   - [ ] Link funcional?

4. **Risco Climático**
   - Subtitle: "Camadas ambientais (chuva/temperatura)"
   - Icon: Cloud ☁️
   - Path: `?view=climate`
   - [ ] Subtitle visível e correto?
   - [ ] Ícone renderizado?
   - [ ] Link funcional?

---

## 2️⃣ VIGILÂNCIA ENTOMOLÓGICA

### **Acesso**: `/modulos/vigilancia-entomologica`

### **Functions Esperadas** (10 total):

#### ✅ ANALISE (5 funções)

1. **Visão Geral**
   - Subtitle: "Panorama de infestação e tendência"
   - Icon: Eye 👁️
   - Path: `?view=overview`
   - [ ] Subtitle visível?

2. **Análise Sazonal**
   - Subtitle: "Séries temporais por município/bairro"
   - Icon: Calendar 📅
   - Path: `?view=sazonal`
   - [ ] Subtitle visível?

3. **Mapa de Calor**
   - Subtitle: "Intensidade e densidade"
   - Icon: Flame 🔥
   - Path: `?view=heatmap`
   - [ ] Subtitle visível?

4. **Hotspots**
   - Subtitle: "Detecção espaço-temporal"
   - Icon: MapPin 📍
   - Path: `?view=hotspots`
   - [ ] Subtitle visível?

5. **Zonas de Risco**
   - Subtitle: "Delimitação e desenho"
   - Icon: AlertTriangle ⚠️
   - Path: `?view=risk`
   - [ ] Subtitle visível?

#### ✅ MAPEAMENTO (3 funções)

6. **Ovitrampas**
   - Subtitle: "Distribuição espacial, reposição e produtividade"
   - Icon: MapPinned 📌
   - Path: `?view=ovitrampas`
   - [ ] Subtitle visível?

7. **Mapa Principal**
   - Subtitle: "Navegação e filtros"
   - Icon: Map 🗺️
   - Path: `?view=mapa`
   - [ ] Subtitle visível?

8. **Camadas (clusters, pontos)**
   - Subtitle: "Camadas e agrupamentos"
   - Icon: Layers 📚
   - Path: `?view=camadas`
   - [ ] Subtitle visível?

#### ✅ INDICADORES (1 função)

9. **Índices (IPO/IDO/IMO)**
   - Subtitle: "Cálculo, metas e ranking"
   - Icon: TrendingUp 📈
   - Path: `?view=indices`
   - [ ] Subtitle visível?

#### ✅ CONTROLE (1 função)

10. **Qualidade**
    - Subtitle: "Completude, consistência e outliers"
    - Icon: CheckCircle ✔️
    - Path: `?view=qualidade`
    - [ ] Subtitle visível?

---

## 3️⃣ VIGILÂNCIA EPIDEMIOLÓGICA

### **Acesso**: `/modulos/vigilancia-epidemiologica`

### **Functions Esperadas** (6 total):

#### ✅ ANALISE (4 funções)

1. **Visão Geral**
   - Subtitle: "Incidência, letalidade, Rt/nowcasting"
   - Icon: Eye 👁️
   - [ ] Subtitle visível?

2. **Nowcasting / Rt**
   - Subtitle: "Transmissibilidade e atraso"
   - Icon: Activity 📊
   - [ ] Subtitle visível?

3. **Séries Temporais**
   - Subtitle: "Casos por semana/município"
   - Icon: LineChart 📉
   - [ ] Subtitle visível?

4. **Hotspots**
   - Subtitle: "Detecção espaço-temporal"
   - Icon: MapPin 📍
   - [ ] Subtitle visível?

#### ✅ MAPEAMENTO (1 função)

5. **Mapa de Incidência**
   - Subtitle: "Choropleth e pontos de casos"
   - Icon: Map 🗺️
   - [ ] Subtitle visível?

#### ✅ CONTROLE (1 função)

6. **Qualidade**
   - Subtitle: "Duplicidades, atraso de notificação"
   - Icon: CheckCircle ✔️
   - [ ] Subtitle visível?

---

## 4️⃣ RESPOSTA OPERACIONAL

### **Acesso**: `/modulos/resposta-operacional`

### **Functions Esperadas** (5 total):

#### ✅ OPERACIONAL (4 funções)

1. **Triagem & Despacho**
   - Subtitle: "Regras de prioridade e distribuição"
   - Icon: ClipboardList 📋
   - Path: `?view=triagem`
   - [ ] Subtitle visível?

2. **Planejamento de Campo**
   - Subtitle: "Roteirização, zonas-alvo"
   - Icon: Calendar 📅
   - Path: `?view=planejamento`
   - [ ] Subtitle visível?

3. **Execução (Mobile)**
   - Subtitle: "Check-ins, coleta e fotos em campo"
   - Icon: Smartphone 📱
   - Path: `?view=execucao`
   - [ ] Subtitle visível?

4. **Acompanhamento**
   - Subtitle: "Status de atividades e produtividade"
   - Icon: CheckSquare ☑️
   - Path: `?view=acompanhamento`
   - [ ] Subtitle visível?

#### ✅ ANALISE (1 função)

5. **Avaliação de Impacto**
   - Subtitle: "Antes/depois por área e período"
   - Icon: Target 🎯
   - Path: `?view=impacto`
   - [ ] Subtitle visível?

---

## 5️⃣ ADMINISTRAÇÃO

### **Acesso**: `/modulos/administracao`

### **Functions Esperadas** (4 total):

#### ✅ CONTROLE (4 funções)

1. **Usuários e Perfis**
   - Subtitle: "Papéis (ADMIN/GESTOR/OPERADOR)"
   - Icon: Users 👥
   - Path: `?view=usuarios`
   - [ ] Subtitle visível?

2. **Parâmetros do Sistema**
   - Subtitle: "Limiares, ícones, camadas default"
   - Icon: Sliders 🎚️
   - Path: `?view=parametros`
   - [ ] Subtitle visível?

3. **Entidades**
   - Subtitle: "Municípios, unidades, equipes"
   - Icon: Building2 🏢
   - Path: `?view=entidades`
   - [ ] Subtitle visível?

4. **Auditoria & Logs**
   - Subtitle: "Trilhas e compliance"
   - Icon: FileSearch 🔍
   - Path: `?view=audit`
   - [ ] Subtitle visível?

---

## 6️⃣ OBSERVABILIDADE

### **Acesso**: `/modulos/observabilidade`

### **Functions Esperadas** (4 total):

#### ✅ CONTROLE (4 funções)

1. **Métricas**
   - Subtitle: "Prometheus/metrics de API e jobs"
   - Icon: Activity 📊
   - Path: `?view=metricas`
   - [ ] Subtitle visível?

2. **Logs**
   - Subtitle: "Estruturados e correlação por request-id"
   - Icon: FileText 📄
   - Path: `?view=logs`
   - [ ] Subtitle visível?

3. **Saúde**
   - Subtitle: "Health checks, filas e storage"
   - Icon: HeartPulse 💓
   - Path: `?view=health`
   - [ ] Subtitle visível?

4. **Qualidade de Dados**
   - Subtitle: "Checks recorrentes e painéis"
   - Icon: ShieldCheck 🛡️
   - Path: `?view=dataQuality`
   - [ ] Subtitle visível?

---

## 🎨 TESTES DE ESTILO

### **Visual**
- [ ] Subtitle aparece ABAIXO do nome da função
- [ ] Subtitle tem cor cinza (#64748b)
- [ ] Subtitle tem tamanho menor (0.625rem)
- [ ] Subtitle tem line-clamp de 2 linhas (trunca se muito longo)
- [ ] Espaçamento adequado entre label e subtitle (margin-top: 0.25rem)

### **Hover**
- [ ] Card eleva ao hover (translateY(-2px))
- [ ] Borda muda de cor ao hover
- [ ] Sombra aumenta ao hover

### **Active State**
- [ ] Card com background azul claro quando ativo
- [ ] Borda azul quando ativo
- [ ] Subtitle muda para cor primária (#0087A8) quando ativo
- [ ] Ícone com background gradiente azul quando ativo

### **Collapsed**
- [ ] Ao clicar no botão de colapsar, painel reduz para 64px
- [ ] Labels, subtitles e categories ficam OCULTOS
- [ ] Apenas ícones visíveis
- [ ] Ícones ficam menores (36px × 36px)

### **Dark Mode**
- [ ] Ativar dark mode (botão lua no header)
- [ ] Background do painel muda para escuro
- [ ] Subtitle muda para cor clara (#94a3b8)
- [ ] Cards com background escuro
- [ ] Contraste adequado

---

## 🚀 TESTES DE FUNCIONALIDADE

### **Navegação**
- [ ] Clicar em cada card e verificar se URL muda
- [ ] Verificar se query params corretos são aplicados (?view=...)
- [ ] Verificar se active state é aplicado na rota correta
- [ ] Browser back/forward funcionando

### **Performance**
- [ ] Painel carrega rapidamente (<1s)
- [ ] Hot-reload funcionando (alterar navigation.css e ver mudanças)
- [ ] Sem erros no console
- [ ] Sem warnings de React

### **Responsividade**
- [ ] Testar em 1920px (desktop)
- [ ] Testar em 1280px (laptop)
- [ ] Testar em 768px (tablet) - painel deve colapsar automaticamente

---

## 📊 RESUMO DE TESTES

### **Total de Functions com Subtítulos**
- Previsão & Simulação: 4
- Vigilância Entomológica: 10
- Vigilância Epidemiológica: 6
- Resposta Operacional: 5
- Administração: 4
- Observabilidade: 4
- **TOTAL: 33 funções**

### **Checklist Final**
- [ ] Todos os 33 subtítulos visíveis e corretos
- [ ] CSS aplicado corretamente (cores, tamanhos, espaçamentos)
- [ ] Comportamento collapsed funcionando
- [ ] Dark mode funcionando
- [ ] Active states funcionando
- [ ] Hovers funcionando
- [ ] Navegação funcional
- [ ] Performance adequada
- [ ] Sem erros no console

---

## 🎯 APROVAÇÃO FINAL

**Testado por**: ___________________  
**Data**: ___________________  
**Status**: [ ] APROVADO [ ] REPROVADO

**Observações**:
_______________________________________________
_______________________________________________
_______________________________________________
