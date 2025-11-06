# ✅ Checklist de Validação - Produção

## 🎯 Objetivo

Validar que o sistema está pronto para produção com autenticação e controle de acesso funcionando corretamente.

---

## 📋 Pré-requisitos

- [ ] Backend rodando (Docker compose up)
- [ ] Keycloak rodando em `http://localhost:8080`
- [ ] Postgres com dados
- [ ] Frontend buildado

---

## 1️⃣ Validar Keycloak e Roles

### 1.1 Verificar Serviços

```bash
# Verificar se Keycloak está respondendo
curl http://localhost:8080/health

# Verificar se backend está respondendo  
curl http://localhost:8000/api/health
```

### 1.2 Testar Usuário Admin com Script

```bash
# Validar token JWT e roles
$env:KC_USER="admin@techdengue.com"
$env:KC_PASS="admin123"
node scripts/ropc-check.js
```

**✅ Resultado esperado**:
```
✓ Login successful!
✓ Token obtido e decodificado

Realm Roles: ADMIN, GESTOR, VIGILANCIA, CAMPO
Client Roles (techdengue-api): (vazio ou com roles específicas)

✓ Usuário admin@techdengue.com tem todas as 4 roles configuradas!
```

**❌ Se falhar**:
- Verificar credenciais no Keycloak
- Verificar se roles foram atribuídas ao usuário
- Ver seção Troubleshooting em `ROLES_E_ACESSO.md`

---

### 1.3 Testar Diferentes Perfis

Validar cada perfil de usuário:

#### Admin (todas roles)
```bash
$env:KC_USER="admin@techdengue.com"
$env:KC_PASS="admin123"
node scripts/ropc-check.js
# Deve ter: ADMIN, GESTOR, VIGILANCIA, CAMPO
```

#### Gestor (gestão e vigilância)
```bash
$env:KC_USER="gestor@techdengue.com"
$env:KC_PASS="gestor123"
node scripts/ropc-check.js
# Deve ter: GESTOR, VIGILANCIA
```

#### Campo (operacional)
```bash
$env:KC_USER="campo@techdengue.com"
$env:KC_PASS="campo123"
node scripts/ropc-check.js
# Deve ter: CAMPO
```

#### Vigilância (técnico)
```bash
$env:KC_USER="vigilancia@techdengue.com"
$env:KC_PASS="vigilancia123"
node scripts/ropc-check.js
# Deve ter: VIGILANCIA
```

---

## 2️⃣ Validar Frontend em Produção

### 2.1 Build de Produção

```bash
npm run build
```

**✅ Verificar**:
- [ ] Sem erros de build
- [ ] Sem warnings críticos
- [ ] Arquivo `dist/index.html` gerado
- [ ] Assets em `dist/assets/`

### 2.2 Verificar Variáveis de Ambiente

```bash
# Ver .env (deve ter DEMO_MODE=false)
cat .env | grep DEMO_MODE
# Esperado: VITE_DEMO_MODE=false
```

**❌ Se estiver true**: corrigir antes de deploy!

### 2.3 Preview do Build

```bash
npm run preview
```

Acessar: `http://localhost:4173`

**✅ Verificar**:
- [ ] Redireciona para `/login`
- [ ] Não permite acesso sem autenticação
- [ ] Logo e branding corretos

---

## 3️⃣ Testar Login e Navegação

### 3.1 Login com Admin

1. Acessar `http://localhost:6080` (dev) ou `http://localhost:4173` (preview)
2. Clicar em **Entrar**
3. Redireciona para Keycloak
4. Login: `admin@techdengue.com` / `admin123`
5. Deve voltar para frontend autenticado

**✅ Verificar**:
- [ ] Token JWT salvo no localStorage
- [ ] User profile disponível no contexto
- [ ] Redirect funcionou corretamente

### 3.2 Validar Menus por Role

#### Como Admin (deve ver TUDO)

- [ ] Dashboard Executivo
- [ ] Mapa Vivo
- [ ] Previsão & Simulação (4 funções)
- [ ] Vigilância Entomológica (10 funções)
- [ ] Vigilância Epidemiológica (6 funções)
- [ ] Resposta Operacional (5 funções)
- [ ] **Administração** (4 funções) ← CRÍTICO
- [ ] **Observabilidade** (4 funções) ← CRÍTICO
- [ ] Relatórios
- [ ] ETL

#### Como Gestor

- [ ] Dashboard Executivo ✅
- [ ] Mapa Vivo ✅
- [ ] Previsão & Simulação ✅
- [ ] Vigilância Epi/Ento ✅
- [ ] Relatórios ✅
- [ ] ❌ Administração (não deve aparecer)
- [ ] ❌ Observabilidade (não deve aparecer)
- [ ] ❌ ETL (não deve aparecer)
- [ ] ❌ Resposta Operacional (não deve aparecer)

#### Como Campo

- [ ] ETL ✅
- [ ] Resposta Operacional ✅
- [ ] Vigilância Entomológica (parcial) ✅
- [ ] ❌ Dashboard (não deve aparecer)
- [ ] ❌ Administração (não deve aparecer)

#### Como Vigilância

- [ ] Vigilância Epi/Ento ✅
- [ ] Mapa Vivo ✅
- [ ] Relatórios ✅
- [ ] ❌ Administração (não deve aparecer)
- [ ] ❌ Dashboard Executivo (não deve aparecer)

---

## 4️⃣ Validar Proteção de Rotas

### 4.1 Tentar Acessar Rota Sem Role

1. Login como `campo@techdengue.com`
2. Tentar acessar manualmente: `http://localhost:6080/modulos/administracao`

**✅ Esperado**:
- Redireciona para home OU
- Mostra tela "Acesso Negado" com mensagem clara

**❌ Se permitir acesso**: bug crítico de segurança!

### 4.2 Verificar No DevTools

Abrir DevTools → Application → Local Storage:

```javascript
// Verificar token
const oidc = localStorage.getItem('oidc.user:...')
const user = JSON.parse(oidc)
console.log('Roles:', user.profile.realm_access.roles)
```

---

## 5️⃣ Testar Fluxos Completos

### 5.1 Fluxo: Admin → Gestão de Usuários

1. Login como admin
2. Sidebar → **Administração**
3. Submenu → **Gestão de Usuários**
4. Deve carregar página (mesmo que placeholder)

**✅ Verificar**:
- [ ] Menu aparece
- [ ] Submenu aparece
- [ ] Função no painel direito aparece
- [ ] Rota carrega

### 5.2 Fluxo: Gestor → Dashboard

1. Login como gestor
2. Sidebar → **Dashboard Executivo**
3. Deve carregar com dados

**✅ Verificar**:
- [ ] Menu aparece
- [ ] Dados carregam (se backend ativo)
- [ ] Gráficos renderizam

### 5.3 Fluxo: Campo → ETL

1. Login como campo
2. Sidebar → **ETL e Integração**
3. Upload de arquivo

**✅ Verificar**:
- [ ] Menu aparece
- [ ] Funcionalidade disponível

---

## 6️⃣ Performance e Segurança

### 6.1 Token Expiration

```bash
# Token deve expirar após 15 minutos (default Keycloak)
# Aguardar 16 minutos e tentar acessar rota protegida
```

**✅ Esperado**:
- Redireciona para login
- Ou renova token silenciosamente (se silent-renew configurado)

### 6.2 Logout

1. Clicar no menu do usuário
2. Clicar em **Sair**

**✅ Verificar**:
- [ ] Redireciona para Keycloak logout
- [ ] Redireciona de volta para home/login
- [ ] Token removido do localStorage
- [ ] Não consegue acessar rotas protegidas

---

## 7️⃣ Testes Automatizados

### 7.1 Suite Completa E2E

```bash
npm run test:e2e
```

**✅ Esperado**: Todos os testes passando

Specs:
- [ ] `navigation.spec.ts` (6+ testes)
- [ ] `roles.spec.ts` (4+ testes)
- [ ] `collapse.spec.ts` (2+ testes)
- [ ] `darkmode.spec.ts` (1+ teste)
- [ ] `mobile.spec.ts` (6 testes)

**Total esperado**: 19+ testes passando

### 7.2 Se Algum Teste Falhar

1. Ver screenshot em `test-results/`
2. Ver vídeo da falha
3. Revisar seletores se mudaram
4. Verificar timing (pode precisar ajustar waits)

---

## 8️⃣ Checklist Final de Deploy

### Antes de Deploy

- [ ] `.env` com `VITE_DEMO_MODE=false`
- [ ] Build sem erros (`npm run build`)
- [ ] Todos E2E passando (`npm run test:e2e`)
- [ ] Keycloak configurado (realm, client, roles)
- [ ] Usuários criados com roles corretas
- [ ] Validação manual de cada perfil (admin, gestor, campo, vigilância)
- [ ] Token expiration testado
- [ ] Logout funcionando
- [ ] Rotas protegidas validadas
- [ ] Sem bypass ativo em produção
- [ ] SSL/HTTPS configurado (se aplicável)

### Pós-Deploy

- [ ] Smoke test: login e navegação básica
- [ ] Verificar logs do Keycloak
- [ ] Verificar logs do backend
- [ ] Monitorar erros no Sentry/similar
- [ ] Testar de diferentes dispositivos
- [ ] Testar de diferentes navegadores

---

## 🐛 Troubleshooting

### Token não contém roles

**Causa**: Roles não atribuídas no Keycloak ou mapeamento errado

**Solução**:
```bash
# Verificar token
node scripts/ropc-check.js

# Se não mostrar roles:
# 1. Keycloak Admin → Users → buscar usuário
# 2. Aba Role Mappings
# 3. Selecionar roles e Add selected
# 4. Fazer logout/login no frontend
```

### Menu não aparece

**Causa**: Role necessária não está no token

**Solução**:
1. Ver documentação `ROLES_E_ACESSO.md`
2. Verificar role necessária para o módulo
3. Atribuir role ao usuário no Keycloak
4. Logout/login

### "Access Denied" inesperado

**Causa**: Rota protegida com role que usuário não tem

**Solução**:
1. Ver `App.tsx` → `requiredRoles` da rota
2. Atribuir role ao usuário ou
3. Ajustar requirement da rota (se erro na config)

---

## 📊 Métricas de Sucesso

Sistema validado com sucesso se:

- ✅ Todos os perfis testados (admin, gestor, campo, vigilância)
- ✅ Menus aparecem/somem conforme esperado
- ✅ Rotas protegidas funcionam
- ✅ Token expiration/renewal funciona
- ✅ Logout funciona
- ✅ 100% dos testes E2E passando
- ✅ Sem erros no console do navegador
- ✅ Sem warnings críticos no build

---

**Validação completa**: Sistema pronto para produção! 🚀

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
