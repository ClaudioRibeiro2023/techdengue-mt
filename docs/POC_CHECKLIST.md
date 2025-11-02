# Checklist de Prova de Conceito (PoC) — TechDengue

**Edital**: CINCOP/MT Pregão Eletrônico 014/2025  
**Natureza**: Obrigatória e Eliminatória (art. 17, § 3º e art. 41, II, Lei 14.133/2021)  
**Prazo**: Notificação 48h antes; apresentação presencial  
**Avaliação**: Comissão técnica com checklist objetivo, pontuação por critério atendido

---

## 1. Preparação (Licitante)

### 1.1 Equipamentos e Infraestrutura
- [ ] Notebooks/computadores (demos web/admin)
- [ ] Smartphones/tablets (demo app móvel)
- [ ] Retroprojetor/TV para apresentação
- [ ] Roteadores/conectividade (4G backup se necessário)
- [ ] Drones/VANTs (opcional: fotos/vídeos se não disponível fisicamente)
- [ ] Sensores/dispositivos IoT (se aplicável)

### 1.2 Datasets de Demonstração
- [ ] Indicadores EPI (CSV municipal, SINAN exemplo, LIRAa exemplo)
- [ ] Atividades de campo (georreferenciadas, status variados)
- [ ] Evidências (fotos com geotag, watermark, hash)
- [ ] Denúncias (simuladas, com triagem automática)
- [ ] Posts redes sociais (dataset offline para Social Listening)
- [ ] Missões de drone (rotas planejadas, cobertura calculada)

### 1.3 Artefatos Documentais
- [ ] Catálogo/prospecto/ficha técnica dos módulos
- [ ] Manual do Usuário (rascunho)
- [ ] Manual do Administrador (rascunho)
- [ ] Arquitetura do sistema (diagrama)
- [ ] Roteiro de apresentação (este checklist)

---

## 2. Itens Obrigatórios da PoC (Conforme TR)

### 2.1 Plataforma Web com Georreferenciamento, Relatórios e Dashboards

#### 2.1.1 Mapa Vivo

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Camadas Base** | Exibir camadas de mapa (OpenStreetMap, satélite, híbrida) | ⬜ | |
| **Georreferenciamento** | Plotar atividades/evidências/indicadores no mapa | ⬜ | |
| **Clustering Inteligente** | Agrupar por criticidade (verde/amarelo/laranja/vermelho/roxo) | ⬜ | |
| **Popups Detalhados** | Clicar em marcador e exibir dados (atividade, SLA, evidências) | ⬜ | |
| **Choropleth** | Camada de incidência/100k ou IPO/IDO/IVO/IMO por município/bairro | ⬜ | |
| **HeatMap** | Camada de calor configurável (intensidade, raio, blur) | ⬜ | |
| **Filtros Temporais** | Filtrar por competência (último dia do mês) ou semana epidemiológica | ⬜ | |
| **Performance** | Demonstrar p95 ≤ 4s com ≥5k feições | ⬜ | Usar Chrome DevTools |

#### 2.1.2 Dashboards Executivos

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Dashboard EPI** | Cartões KPI (casos, incidência, IPO/IDO/IVO/IMO), tendência (gráfico linhas) | ⬜ | |
| **Dashboard Operacional** | SLA (% no prazo), produtividade (atividades/dia), pendências | ⬜ | |
| **Drill-Down** | Clicar em KPI e filtrar mapa/lista de atividades | ⬜ | |
| **Atualização em Tempo Real** | Simular nova atividade e atualizar dashboard (WebSocket ou polling) | ⬜ | |

#### 2.1.3 Relatórios Automatizados

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **EPI01 (PDF/A-1)** | Gerar relatório epidemiológico com município, competência, gráficos, hash | ⬜ | Validar PDF/A-1 |
| **EVD01 (PDF/A-1)** | Gerar relatório de evidências de atividade com miniaturas, metadados, root hash | ⬜ | |
| **CSV Export** | Exportar indicadores EPI em CSV (compatível CSV-EPI01) | ⬜ | |
| **GeoJSON Export** | Exportar atividades com DLP/RBAC (mascaramento de campos sensíveis) | ⬜ | |
| **Hash no Rodapé** | Verificar SHA-256 no rodapé dos PDFs | ⬜ | |

---

### 2.2 Aplicativo Móvel com Chatbot, Canal de Denúncia e Integração Vigilância

#### 2.2.1 App Móvel (PWA ou Nativo)

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Login SSO** | Autenticar via OIDC (ou simular) | ⬜ | |
| **Agenda de Atividades** | Listar atividades atribuídas ao agente | ⬜ | |
| **Checklist Dinâmico** | Executar checklist de atividade (itens condicionais) | ⬜ | |
| **Captura de Evidências** | Tirar foto com geotag, watermark automático, cálculo SHA-256 local | ⬜ | Exibir coordenadas |
| **Offline-First** | Demonstrar operação sem internet (IndexedDB + fila de sync) | ⬜ | Ativar modo avião |
| **Sincronização** | Voltar online e sincronizar atividades/evidências pendentes | ⬜ | |
| **Insumos** | Registrar baixa de insumos (lote, validade, quantidade) | ⬜ | Bloquear vencidos |

#### 2.2.2 Chatbot (Canal de Denúncia)

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Fluxo Conversacional** | Iniciar conversa: "Olá! Vi um foco de mosquito..." | ⬜ | FSM local |
| **Coleta de Localização** | Chatbot pede endereço ou coordenadas | ⬜ | |
| **Coleta de Tipo de Foco** | Opções: caixa d'água, pneu, lixo, outro | ⬜ | |
| **Coleta de Descrição** | Texto livre descrevendo o foco | ⬜ | |
| **Upload de Foto (Opcional)** | Anexar foto do foco | ⬜ | |
| **Confirmação** | Chatbot resume dados e pede confirmação | ⬜ | |
| **Triagem Automática** | Criar `atividade` (origem='DENUNCIA', status='CRIADA') | ⬜ | Exibir no mapa |
| **Handoff** | Se chatbot não resolver, redirecionar para formulário detalhado | ⬜ | |

---

### 2.3 Sistema de Inteligência Artificial com Robôs Virtuais em Redes Sociais

#### 2.3.1 Social Listening (PoC Simulado)

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Dataset Offline** | Exibir tweets/posts sintéticos sobre dengue (50-100 exemplos) | ⬜ | Sem APIs externas |
| **Palavras-Chave** | Detectar "dengue", "picada", "mosquito", "foco", "água parada" | ⬜ | Highlight na UI |
| **Classificação de Sentimento** | Negativo (reclamação), Neutro (info), Positivo (elogio) | ⬜ | Exibir score |
| **Extração de Localização** | Identificar município/bairro mencionado no texto | ⬜ | NLP básico |
| **Geração de Alertas** | Posts negativos + localização → criar `atividade` (origem='ALERTA') | ⬜ | |
| **Dashboard** | Mapa de calor de menções, linha do tempo, top hashtags | ⬜ | |
| **Nota de Limitação** | Esclarecer que é PoC simulado (produção requer APIs autorizadas) | ⬜ | |

---

### 2.4 Demonstração de Integração com SINAN e LIRAa

#### 2.4.1 Conectores PoC

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **CSV SINAN Exemplo** | Carregar CSV público SINAN Arboviroses (casos notificados) | ⬜ | |
| **CSV LIRAa Exemplo** | Carregar CSV LIRAa (IIP, IBR por município) | ⬜ | |
| **Normalização** | Mapear campos para `indicador_epi` (fonte='SINAN'/'LIRAa') | ⬜ | |
| **Validação** | Validar códigos IBGE, competências, valores numéricos | ⬜ | Relatório de qualidade |
| **Carga** | Inserir dados na tabela `indicador_epi` | ⬜ | |
| **Visualização** | Exibir indicadores importados no mapa/dashboard | ⬜ | |
| **Nota de Integração Real** | Esclarecer que produção usará APIs oficiais (se disponíveis) ou ETL agendado | ⬜ | |

---

### 2.5 Simulação de Plano de Voo e Operação VANTs (Drones) com Dispersão de Larvicidas

#### 2.5.1 Planejador de Missão

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Seleção de Área** | Desenhar polígono no mapa (área de tratamento) | ⬜ | |
| **Parâmetros de Voo** | Altitude (m), padrão (grid/serpentina), velocidade (m/s) | ⬜ | |
| **Cálculo de Cobertura** | Área (ha), autonomia drone, taxa de dispersão larvicida (L/ha) | ⬜ | Exibir na tela |
| **Geração de Waypoints** | Criar rota otimizada (lista de coordenadas) | ⬜ | |
| **Validação de Regras** | Verificar zonas proibidas (ANAC), distância de aeroportos | ⬜ | Alerta se violar |
| **Export de Rota** | Baixar KML/GeoJSON para uso em controlador drone | ⬜ | |
| **Simulação de Missão** | Animar rota no mapa 3D, status (em voo/dispersão/retorno), logs | ⬜ | Acelerado 10x |
| **Dashboard de Missões** | Histórico, cobertura acumulada (ha), insumos consumidos (L) | ⬜ | |
| **Nota de Operação Real** | Esclarecer que é simulador (produção requer drone real + telemetria) | ⬜ | |

---

### 2.6 Controle de Acesso, Trilha de Auditoria e Segurança da Informação

#### 2.6.1 Autenticação e Autorização (OIDC/RBAC)

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Login SSO** | Autenticar via OIDC (Keycloak, Auth0 ou mock) | ⬜ | |
| **Papéis e Escopos** | Demonstrar 4 papéis (GESTOR, VIGILANCIA, CAMPO, ADMIN) | ⬜ | |
| **RBAC Funcional** | GESTOR: só leitura; CAMPO: CRUD atividades; ADMIN: tudo | ⬜ | Tentar ação não permitida |
| **Token JWT** | Exibir token (claims: sub, papel, escopos, exp) | ⬜ | DevTools ou Postman |
| **Renovação de Sessão** | Refresh token ou re-autenticação | ⬜ | |

#### 2.6.2 Trilha de Auditoria

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Tabela `audit_log`** | Registrar ações (CREATE/UPDATE/EXPORT/LOGIN) | ⬜ | |
| **Payload Resumido** | Campos alterados, metadados (IP, user-agent, timestamp) | ⬜ | |
| **Consulta de Auditoria** | Buscar logs por usuário, recurso, ação, período | ⬜ | UI Admin |
| **Imutabilidade** | Logs são append-only (sem DELETE) | ⬜ | Confirmar esquema DB |

#### 2.6.3 Segurança da Informação

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **HTTPS** | Tráfego criptografado (TLS 1.2+) | ⬜ | Certificado válido |
| **Headers de Segurança** | HSTS, X-Frame-Options, CSP, X-Content-Type-Options | ⬜ | curl -I ou DevTools |
| **DLP em Exports** | Mascarar campos sensíveis (comentários privados, CPF se houver) | ⬜ | Export GeoJSON |
| **Rate Limiting** | Bloquear após N requisições/min (ex: 100/min) | ⬜ | Testar com script |
| **Validação de Entrada** | Sanitização de SQL injection, XSS, path traversal | ⬜ | OWASP Top 10 |
| **Secrets Management** | Não expor chaves/senhas em logs ou código-fonte | ⬜ | Env vars ou vault |

---

### 2.7 Geração e Visualização de Relatórios com Filtros Dinâmicos e Exportação de Dados

#### 2.7.1 Filtros Dinâmicos

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **Filtro por Município** | Dropdown/autocomplete com lista de municípios | ⬜ | |
| **Filtro por Competência** | Date picker (último dia do mês) ou semana epidemiológica | ⬜ | |
| **Filtro por Status** | Atividades: CRIADA, EM_ANDAMENTO, ENCERRADA | ⬜ | |
| **Filtro por Equipe** | Listar equipes e filtrar atividades atribuídas | ⬜ | |
| **Filtro por Indicador** | Escolher IPO, IDO, IVO, IMO, incidência/100k | ⬜ | |
| **Aplicação em Tempo Real** | Mapa e listas atualizam sem reload de página | ⬜ | |

#### 2.7.2 Exportações

| Critério | Descrição | Status | Observações |
|---|---|---|---|
| **EPI01 (PDF+CSV)** | Botão "Gerar EPI01" → baixar PDF e CSV | ⬜ | Hash visível |
| **EVD01 (PDF)** | Botão "Gerar EVD01" para atividade → baixar PDF | ⬜ | Miniaturas, root hash |
| **GeoJSON** | Botão "Exportar Atividades" → baixar .geojson | ⬜ | DLP aplicado |
| **CSV Personalizado** | Exportar lista filtrada (indicadores, atividades) | ⬜ | Colunas selecionáveis |
| **Verificação de Hash** | Calcular SHA-256 do PDF baixado e comparar com rodapé | ⬜ | Usar `sha256sum` |

---

## 3. Critérios de Avaliação (Comissão Técnica)

### 3.1 Pontuação Objetiva

| Item | Peso | Atendimento | Pontos |
|---|---|---|---|
| **2.1 Plataforma Web** | 25% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/25 |
| **2.2 App Móvel + Chatbot** | 20% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/20 |
| **2.3 Social Listening (IA)** | 10% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/10 |
| **2.4 Integração SINAN/LIRAa** | 10% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/10 |
| **2.5 Drone Simulator** | 10% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/10 |
| **2.6 Segurança/Auditoria** | 15% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/15 |
| **2.7 Relatórios/Exports** | 10% | ⬜ Pleno ⬜ Parcial ⬜ Não | __/10 |
| **Total** | 100% | | __/100 |

### 3.2 Critério de Aprovação

- **Aprovado**: Pontuação ≥ 80/100 e nenhum item crítico com "Não Atendimento".
- **Reprovado**: Pontuação < 80/100 ou item crítico não atendido.
- **Itens Críticos**: 2.1 (Plataforma Web), 2.6 (Segurança/Auditoria), 2.7 (Relatórios com hash).

---

## 4. Laudo de Aceitabilidade (Template)

### 4.1 Informações da PoC

- **Licitante**: [Nome da Empresa]
- **Data**: [DD/MM/YYYY]
- **Horário**: [HH:MM]
- **Local**: [Sede CINCOP-MT ou outro]
- **Comissão Técnica**: [Nomes dos membros]

### 4.2 Resultado da Avaliação

- **Pontuação Final**: __/100
- **Status**: ⬜ Aprovado ⬜ Reprovado
- **Observações**:
  - [Listar pontos fortes]
  - [Listar não conformidades, se houver]
  - [Recomendações para produção]

### 4.3 Assinaturas

- **Presidente da Comissão**: ________________________
- **Membro 1**: ________________________
- **Membro 2**: ________________________
- **Membro 3**: ________________________

---

## 5. Pós-PoC

### 5.1 Se Aprovado
- [ ] Emitir Laudo de Aceitabilidade
- [ ] Habilitar licitante para adjudicação
- [ ] Prosseguir com assinatura de Ata de Registro de Preços

### 5.2 Se Reprovado
- [ ] Emitir Laudo com justificativa detalhada
- [ ] Convocar licitante subsequente (se houver)
- [ ] Repetir PoC com novo licitante
- [ ] Se nenhum atender: anular licitação ou rever TR

### 5.3 Retirada de Equipamentos
- [ ] Licitante tem 10 dias para retirar equipamentos usados na PoC
- [ ] Após prazo: CINCOP-MT pode descartar ou incorporar

---

**Fim do Checklist de PoC**

---

**Referências**:
- Edital CINCOP/MT Pregão 014/2025
- ANEXO I — Termo de Referência
- Lei Federal 14.133/2021 (art. 17, § 3º e art. 41, II)
- `docs/PLANO_DE_IMPLEMENTACAO.md` (Fase P)
- `docs/CADERNO_DE_TESTES.md` (casos de teste detalhados)
