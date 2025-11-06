# 🧪 Guia Rápido de Teste - Módulo e-Denúncia

**Tempo estimado**: 5-10 minutos  
**Pré-requisito**: Backend e frontend rodando

---

## 🚀 Iniciar Serviços

```bash
# 1. Backend (se não estiver rodando)
cd infra
docker compose up -d
# Aguardar ~30 segundos para migrations

# 2. Frontend
cd ../frontend
npm run dev
# Abre em http://localhost:6080
```

---

## ✅ Checklist de Testes

### 1️⃣ Acesso à Página (30 segundos)

```
URL: http://localhost:6080/denuncia

✓ Página carrega sem erros
✓ Título "e-Denúncia - Reporte Focos de Dengue" aparece
✓ Chatbot inicializa com primeira pergunta
✓ Botão "Denunciar" (laranja) visível no header
```

### 2️⃣ Chatbot FSM (1 minuto)

**Cenário A - Prioridade ALTA**
```
1. "Você viu água parada?" → Clique "Sim"
2. "Há larvas visíveis?" → Clique "Sim, vejo larvas"
3. Resultado: 🔴 Prioridade ALTA
   ✓ Mensagem: "Larvas visíveis indicam risco iminente"
   ✓ Transição para formulário após 2 segundos
```

**Cenário B - Prioridade MÉDIA**
```
1. "Você viu água parada?" → Clique "Sim"
2. "Há larvas visíveis?" → Clique "Não vejo larvas"
3. Resultado: 🟡 Prioridade MÉDIA
   ✓ Mensagem: "Situação requer atenção"
```

**Cenário C - Prioridade BAIXA**
```
1. "Você viu água parada?" → Clique "Não"
2. "Há lixo acumulado?" → Clique "Não há lixo"
3. Resultado: 🟢 Prioridade BAIXA
   ✓ Mensagem: "Denúncia registrada"
```

### 3️⃣ Formulário (2 minutos)

```
GPS:
✓ Status aparece: "Capturando localização GPS..."
✓ Após alguns segundos: "✓ Localização capturada (precisão: Xm)"
   ⚠️ Se erro: Autorize no navegador ou clique "Tentar novamente"

Preencher:
- Município: Selecionar "Cuiabá" (ou qualquer outro)
- Endereço: "Rua das Flores, 123"
- Bairro: "Centro"
- Descrição: "Teste do sistema e-Denúncia. Pneu com água parada."

Foto (opcional):
✓ Clique "Adicionar foto"
✓ Selecione imagem (max 5MB)
✓ Preview aparece

Contato:
- Marcar "Prefiro manter anonimato" OU
- Nome: "Teste Sistema"
- Telefone: "65 98765-4321"

Botões:
✓ "Voltar" - retorna ao chatbot
✓ "Enviar Denúncia" - ativo se GPS OK
```

### 4️⃣ Submissão (30 segundos)

```
Clique "Enviar Denúncia"

✓ Loading: "Enviando denúncia..."
✓ Tela de sucesso aparece:
   - ✅ Denúncia Registrada!
   - Protocolo: DEN-YYYYMMDD-NNNN
   - Botões: "Voltar para Home" | "Fazer Nova Denúncia"
```

### 5️⃣ Validação Backend (1 minuto)

```bash
# Ver denúncias no banco
curl http://localhost:8000/api/denuncias | jq '.[0]'

# Consultar por protocolo (use o recebido)
curl http://localhost:8000/api/denuncias/DEN-20251103-0001 | jq

# Verificar atividade criada (se foi prioridade ALTA)
# Acesse http://localhost:6080/atividades
# Deve aparecer: "Denúncia DEN-XXXXXXXX-XXXX - Foco de Aedes"
```

### 6️⃣ Database (1 minuto)

```bash
# Conectar ao PostgreSQL
docker exec -it techdengue-db psql -U postgres -d techdengue

# Queries
SELECT numero_protocolo, status, chatbot_classificacao, municipio_nome
FROM denuncias_publicas
ORDER BY criado_em DESC
LIMIT 5;

# Ver atividades criadas
SELECT a.titulo, a.prioridade, d.numero_protocolo
FROM atividades a
JOIN denuncias_publicas d ON d.atividade_id = a.id
WHERE a.origem = 'DENUNCIA';

# Estatísticas
SELECT 
    chatbot_classificacao,
    COUNT(*) as total,
    COUNT(atividade_id) as com_atividade
FROM denuncias_publicas
GROUP BY chatbot_classificacao;
```

---

## 🐛 Troubleshooting

### GPS não funciona

```
Erro: "Não foi possível obter sua localização"

Soluções:
1. Autorize no navegador (popup aparece no topo)
2. Chrome: Configurações → Privacidade → Configurações do site → Localização
3. Use HTTPS em produção (HTTP só funciona em localhost)
4. Fallback: Continuar sem GPS (será adicionado em próxima versão)
```

### Erro ao enviar

```
Erro 400: "Código IBGE inválido"
→ Verifique se município existe na tabela municipios_ibge

Erro 500: "Erro ao criar denúncia"
→ Verifique logs do backend:
   docker logs techdengue-epi-api --tail 50

Erro CORS:
→ Verifique middleware/security.py
→ Porta 6080 deve estar em allowed_origins
```

### Migration não aplicada

```bash
# Verificar versão da migration
docker exec techdengue-db psql -U postgres -d techdengue \
  -c "SELECT version FROM flyway_schema_history ORDER BY installed_rank DESC LIMIT 5;"

# Se V013 não aparece:
docker compose -f infra/docker-compose.yml restart epi-api
# Aguardar 30 segundos
```

### Frontend não compila

```bash
cd frontend

# Limpar e reinstalar
rm -rf node_modules
npm install

# Verificar erros TypeScript
npm run type-check

# Rebuild
npm run dev
```

---

## 📊 Critérios de Sucesso

| Item | Esperado | Status |
|------|----------|--------|
| Página carrega | ✅ Sem erros 404/500 | ☐ |
| Chatbot funciona | ✅ Classifica em 3 níveis | ☐ |
| GPS captura | ✅ Coordenadas obtidas | ☐ |
| Formulário valida | ✅ Campos obrigatórios | ☐ |
| Protocolo gerado | ✅ Formato DEN-YYYYMMDD-NNNN | ☐ |
| Insert no banco | ✅ Registro em denuncias_publicas | ☐ |
| Atividade criada | ✅ Se prioridade ALTA | ☐ |
| API responde | ✅ GET /api/denuncias OK | ☐ |

---

## 🎯 Casos de Teste Completos

### Teste 1: Denúncia ALTA com Foto

```
1. Chatbot: Água parada SIM → Larvas SIM
2. GPS: Autorizar e capturar
3. Formulário: Preencher todos campos + foto
4. Submeter
5. Validar: Protocolo recebido
6. Verificar: Atividade criada automaticamente
```

### Teste 2: Denúncia MÉDIA Anônima

```
1. Chatbot: Água parada NÃO → Lixo SIM
2. GPS: Autorizar
3. Formulário: Preencher + marcar "anonimato"
4. Submeter
5. Validar: Sem nome/telefone na resposta
```

### Teste 3: Denúncia BAIXA sem Foto

```
1. Chatbot: Água parada NÃO → Lixo NÃO
2. GPS: Autorizar
3. Formulário: Apenas campos obrigatórios
4. Submeter
5. Validar: Status PENDENTE (sem atividade)
```

### Teste 4: Consulta por Protocolo

```
1. Criar denúncia qualquer
2. Anotar protocolo (ex: DEN-20251103-0001)
3. curl http://localhost:8000/api/denuncias/DEN-20251103-0001
4. Validar: Dados retornam corretamente
```

### Teste 5: Estatísticas

```
1. Criar 3 denúncias (ALTA, MÉDIA, BAIXA)
2. curl http://localhost:8000/api/denuncias/stats/resumo
3. Validar: Contadores corretos
```

---

## 📸 Screenshots Esperados

### Tela 1: Chatbot Inicial
```
┌─────────────────────────────────────┐
│ 🦟 Assistente de Triagem            │
│ Vou ajudar a classificar...         │
├─────────────────────────────────────┤
│ Bot: 🚨 Vamos identificar a         │
│      gravidade. Você viu água...    │
├─────────────────────────────────────┤
│ Selecione uma opção:                │
│ [Sim]                     →         │
│ [Não]                     →         │
└─────────────────────────────────────┘
```

### Tela 2: Resultado Classificação
```
┌─────────────────────────────────────┐
│ 🔴 Prioridade ALTA                  │
│                                     │
│ Larvas visíveis indicam risco       │
│ iminente. Equipe será acionada      │
│ rapidamente.                        │
└─────────────────────────────────────┘
```

### Tela 3: Formulário
```
┌─────────────────────────────────────┐
│ Dados da Denúncia                   │
├─────────────────────────────────────┤
│ ✓ Localização capturada (10m)      │
│                                     │
│ Município: [Cuiabá          ▼]     │
│ Endereço: [________________]       │
│ Bairro:   [________________]       │
│ Descrição: [________________]      │
│            [________________]       │
│                                     │
│ [📷 Adicionar foto]                │
│                                     │
│ □ Prefiro manter anonimato         │
│                                     │
│ [Voltar] [Enviar Denúncia]         │
└─────────────────────────────────────┘
```

### Tela 4: Sucesso
```
┌─────────────────────────────────────┐
│         ✅                          │
│   Denúncia Registrada!              │
│                                     │
│ Sua denúncia foi recebida e será   │
│ analisada em breve.                 │
│                                     │
│ ┌─────────────────────────────┐   │
│ │ Número do Protocolo         │   │
│ │ DEN-20251103-0001          │   │
│ │ Guarde este número          │   │
│ └─────────────────────────────┘   │
│                                     │
│ [Voltar para Home]                 │
│ [Fazer Nova Denúncia]              │
└─────────────────────────────────────┘
```

---

## ⏱️ Performance Esperada

| Métrica | Valor Esperado |
|---------|----------------|
| Carregamento página | < 2s |
| Resposta chatbot | < 200ms |
| Captura GPS | 2-5s |
| Submit formulário | < 1s |
| Insert database | < 500ms |
| Geração protocolo | < 100ms |
| Total (fim a fim) | 3-5 min |

---

## 🎓 Checklist Final PoC

- [ ] Todos os 5 testes completos executados
- [ ] GPS funciona em 100% das tentativas
- [ ] Protocolo gerado em formato correto
- [ ] Denúncias visíveis no banco
- [ ] Atividades criadas para prioridade ALTA
- [ ] API endpoints respondem corretamente
- [ ] Sem erros no console (browser ou backend)
- [ ] Documentação `MODULO_E_DENUNCIA.md` revisada

---

## 📝 Report de Teste

```markdown
# Report: Teste e-Denúncia
Data: YYYY-MM-DD
Testador: [Nome]

## Resultado Geral
✅ PASSOU | ❌ FALHOU

## Detalhes
1. Acesso página: ✅
2. Chatbot FSM: ✅
3. GPS captura: ✅
4. Formulário: ✅
5. Submissão: ✅
6. Backend: ✅
7. Database: ✅

## Bugs Encontrados
- [ ] Nenhum
- [ ] [Descrever bug]

## Observações
[Comentários adicionais]
```

---

**Boa sorte nos testes! 🚀**

Se encontrar problemas, consulte `docs/MODULO_E_DENUNCIA.md` para troubleshooting detalhado.
