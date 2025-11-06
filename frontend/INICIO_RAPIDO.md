# 🚀 Início Rápido - TechDengue Frontend

## ⚡ Setup em 2 Minutos

### Pré-requisitos

- ✅ Node.js 18+ instalado
- ✅ npm ou yarn
- ⚠️ Keycloak rodando (para produção) ou usar modo DEMO

---

## 🎯 Opção 1: Modo DEMO (Sem Backend)

**Ideal para**: Desenvolvimento de UI, testes visuais

### Passo 1: Instalar dependências

```bash
cd frontend
npm install
```

### Passo 2: Configurar modo DEMO

Criar arquivo `.env.development`:

```env
VITE_DEMO_MODE=true
VITE_API_URL=http://localhost:8000/api
```

### Passo 3: Rodar aplicação

```bash
npm run dev
```

**Pronto!** Aplicação rodando em: **http://localhost:6080**

**Características do modo DEMO**:
- ✅ Sem autenticação necessária
- ✅ Usuário mockado com todas as roles
- ✅ Navegação completa liberada
- ✅ Hot reload ativo
- ⚠️ Dados mockados (não salva no banco)

---

## 🔐 Opção 2: Modo Produção (Com Backend)

**Ideal para**: Desenvolvimento completo, testes integrados

### Passo 1: Instalar dependências

```bash
cd frontend
npm install
```

### Passo 2: Iniciar Backend

```bash
# Em outro terminal, na raiz do projeto
docker-compose up -d
```

**Aguardar ~30 segundos** para todos os serviços iniciarem.

### Passo 3: Verificar serviços

```bash
# Verificar se estão rodando
curl http://localhost:8080  # Keycloak
curl http://localhost:8000/api/health  # Backend API
```

### Passo 4: Configurar Keycloak

**Opção A: Usar configuração existente**
```bash
# Se já configurado anteriormente, pular este passo
```

**Opção B: Configurar do zero**
```bash
# Seguir guia: docs/KEYCLOAK_SETUP_RAPIDO.md
# Tempo: ~5 minutos
```

### Passo 5: Configurar variáveis de ambiente

Criar arquivo `.env.development`:

```env
VITE_DEMO_MODE=false
VITE_API_URL=http://localhost:8000/api
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=techdengue
VITE_KEYCLOAK_CLIENT_ID=techdengue-frontend
```

### Passo 6: Rodar aplicação

```bash
npm run dev
```

**Pronto!** Aplicação rodando em: **http://localhost:6080**

**Login**: Usar credenciais configuradas no Keycloak
- Exemplo: `admin@techdengue.com` / `admin123`

---

## 🧪 Modo E2E (Testes)

**Ideal para**: Rodar testes automatizados

### Passo 1: Instalar Playwright

```bash
npx playwright install
```

### Passo 2: Rodar testes

```bash
# Todos os testes
npm run test:e2e

# Com UI interativa
npm run test:e2e:ui

# Com browser visível
npm run test:e2e:headed

# Debug mode
npm run test:e2e:debug
```

**Modo E2E características**:
- ✅ Bypass de autenticação automático
- ✅ Roles simuladas via query params
- ✅ 200+ testes em ~5 minutos
- ✅ Relatórios automáticos

---

## 📋 Comandos Úteis

### Desenvolvimento

```bash
# Rodar em modo desenvolvimento
npm run dev

# Build para produção
npm run build

# Preview do build
npm run preview

# Verificar tipos TypeScript
npm run typecheck

# Lint do código
npm run lint
```

### Testes

```bash
# Todos os testes E2E
npm run test:e2e

# Apenas um spec
npx playwright test navigation.spec.ts

# Apenas browser específico
npx playwright test --project=chromium

# Apenas mobile
npx playwright test mobile.spec.ts --project=mobile-chrome
```

### Utilitários

```bash
# Verificar roles no Keycloak
npm run ropc:check

# Limpar cache
rm -rf node_modules/.vite

# Reinstalar dependências
rm -rf node_modules package-lock.json
npm install
```

---

## 🔧 Troubleshooting

### Problema: `npm run dev` não inicia

**Causa**: Node.js desatualizado

**Solução**:
```bash
node --version  # Deve ser >= 18
nvm use 18      # Se usar nvm
```

---

### Problema: Erro de porta já em uso

**Causa**: Porta 6080 ocupada

**Solução**:
```bash
# Windows
netstat -ano | findstr :6080
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:6080 | xargs kill -9
```

---

### Problema: Keycloak não responde

**Causa**: Container não iniciado

**Solução**:
```bash
docker ps  # Verificar se keycloak está UP
docker logs keycloak  # Ver logs

# Reiniciar se necessário
docker-compose restart keycloak
```

---

### Problema: "Failed to fetch" ao fazer login

**Causa**: Keycloak ou API não acessível

**Solução**:
```bash
# Verificar URLs no .env
cat .env.development

# Testar conectividade
curl http://localhost:8080
curl http://localhost:8000/api/health
```

---

### Problema: Tela branca após login

**Causa**: Roles não configuradas no Keycloak

**Solução**:
```bash
# Seguir: docs/KEYCLOAK_SETUP_RAPIDO.md
# Seção "Atribuir Roles ao Usuário"
```

---

## 🎨 Desenvolvimento Visual

### Acessar em diferentes modos

```bash
# Modo DEMO (sem auth)
http://localhost:6080

# Modo E2E com role específica
http://localhost:6080/?e2e-roles=ADMIN
http://localhost:6080/?e2e-roles=GESTOR
http://localhost:6080/?e2e-roles=CAMPO

# Múltiplas roles
http://localhost:6080/?e2e-roles=ADMIN,GESTOR
```

### Dark Mode

Ativar via toggle no header ou:

```javascript
// Console DevTools
document.documentElement.classList.add('theme-dark')
```

### Testar permissões

```javascript
// Console DevTools
localStorage.setItem('e2e-roles', JSON.stringify(['CAMPO']))
location.reload()
```

---

## 📊 Verificar Status do Sistema

### Frontend

```bash
# Aplicação rodando?
curl http://localhost:6080

# Versão
cat package.json | grep version
```

### Backend (se usando)

```bash
# API
curl http://localhost:8000/api/health

# Keycloak
curl http://localhost:8080

# Banco de dados
docker exec -it postgres psql -U postgres -c "SELECT version();"
```

---

## 🚀 Deploy Local (Build de Produção)

```bash
# 1. Build
npm run build

# 2. Preview
npm run preview

# Ou usar servidor estático
npx serve -s dist -l 4173
```

**Build estará em**: `dist/`

---

## 📚 Documentação Completa

- **Setup Completo**: `docs/README.md`
- **Keycloak**: `docs/KEYCLOAK_SETUP_RAPIDO.md`
- **Roles**: `docs/ROLES_E_ACESSO.md`
- **Permissões**: `docs/PERMISSOES_GRANULARES.md`
- **UX Components**: `docs/UX_FEEDBACK_ROLES.md`
- **CI/CD**: `docs/CI_CD_PIPELINE.md`
- **Sentry**: `docs/SENTRY_SETUP.md`
- **E2E**: `docs/E2E_SUITE_COMPLETA.md`

---

## ⚡ Atalhos Rápidos

| Ação | Comando |
|------|---------|
| **Iniciar (DEMO)** | `npm run dev` |
| **Iniciar (Prod)** | `docker-compose up -d && npm run dev` |
| **Testes** | `npm run test:e2e:ui` |
| **Build** | `npm run build` |
| **Preview** | `npm run preview` |
| **Logs** | Browser DevTools → Console |
| **Debug E2E** | `npm run test:e2e:debug` |

---

## 🎯 Checklist de Inicialização

### Modo DEMO
- [ ] Node.js 18+ instalado
- [ ] `npm install` executado
- [ ] `.env.development` criado com `VITE_DEMO_MODE=true`
- [ ] `npm run dev` rodando
- [ ] Abrir http://localhost:6080
- [ ] ✅ Sistema operacional!

### Modo Produção
- [ ] Node.js 18+ instalado
- [ ] Docker instalado e rodando
- [ ] `npm install` executado
- [ ] `docker-compose up -d` executado
- [ ] Keycloak configurado (usuário + roles)
- [ ] `.env.development` criado com credenciais corretas
- [ ] `npm run dev` rodando
- [ ] Login com usuário do Keycloak
- [ ] ✅ Sistema operacional!

---

**Dúvidas?** Consulte `docs/README.md` ou abra uma issue.

**Última atualização**: 06/11/2025
