# 🚀 Guia de Deploy - TechDengue MT

## 📊 Visão Geral

Guia completo para deploy da aplicação TechDengue MT no **Netlify** (frontend) com integração **GitHub** para CI/CD automático.

**Status**: ✅ Pronto para Deploy  
**Data**: 2024-11-02  
**Versão**: 1.0.0

---

## 🎯 Arquitetura de Deploy

```
┌──────────────────────────────────────────────────────────────┐
│                         DEPLOY                                │
├──────────────────────────────────────────────────────────────┤
│                                                               │
│  GitHub Repository                                            │
│  ├── main branch → Netlify Production                        │
│  ├── develop branch → Netlify Preview                        │
│  └── pull_requests → Netlify Deploy Previews                 │
│                                                               │
│  GitHub Actions (CI)                                          │
│  ├── Lint + TypeCheck                                        │
│  ├── Build                                                    │
│  └── E2E Tests (PRs)                                          │
│                                                               │
│  Netlify (Frontend)                                           │
│  ├── Build: npm run build                                    │
│  ├── Publish: dist/                                          │
│  ├── SPA Redirects                                            │
│  └── Security Headers                                         │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

---

## 📋 Pré-requisitos

- [x] Conta GitHub
- [x] Conta Netlify
- [x] Git instalado localmente
- [x] Node.js 18+ instalado

---

## 🔧 Passo 1: Integração com GitHub

### 1.1 Inicializar Repositório Git (se ainda não foi feito)

```bash
cd c:\Users\claud\CascadeProjects\Techdengue_MT

# Inicializar git
git init

# Adicionar origin (substitua com seu repo)
git remote add origin https://github.com/SEU_USUARIO/techdengue-mt.git
```

### 1.2 Verificar .gitignore

O arquivo `.gitignore` deve incluir:

```gitignore
# Dependencies
node_modules/
**/node_modules/

# Build outputs
dist/
build/
.next/
out/

# Environment variables
.env
.env.local
.env.*.local
**/.env

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
coverage/
.nyc_output/
playwright-report/
test-results/

# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
*.egg-info/
```

### 1.3 Fazer Commit Inicial

```bash
# Adicionar todos os arquivos
git add .

# Commit inicial
git commit -m "feat: initial commit - TechDengue MT v1.0

- Backend completo (35 endpoints)
- Frontend PWA (React + TypeScript)
- Testes E2E (Playwright)
- Performance tests (k6)
- Security hardening
- Documentation completa"

# Push para GitHub
git push -u origin main
```

### 1.4 Criar Branch Develop

```bash
# Criar e mudar para branch develop
git checkout -b develop

# Push develop
git push -u origin develop
```

---

## 🚀 Passo 2: Deploy no Netlify

### 2.1 Criar Conta e Importar Repositório

1. **Acesse**: <https://app.netlify.com/>
2. **Sign up** com GitHub
3. **Add new site** → **Import an existing project**
4. **Connect to Git provider** → Selecione **GitHub**
5. **Authorize Netlify** no GitHub
6. **Pick a repository** → Selecione `techdengue-mt`

### 2.2 Configurar Build Settings

Na tela de configuração do site:

**Basic build settings**:
```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/dist
```

**Build settings** (avançado):
- Node version: `18`
- Package manager: `npm`

### 2.3 Configurar Environment Variables

Em **Site settings** → **Environment variables**, adicione:

| Variable | Value | Description |
|----------|-------|-------------|
| `VITE_API_URL` | `https://api.techdengue.mt.gov.br/api` | URL da API backend |
| `VITE_KEYCLOAK_URL` | `https://keycloak.techdengue.mt.gov.br` | URL do Keycloak |
| `VITE_KEYCLOAK_REALM` | `techdengue` | Realm do Keycloak |
| `VITE_KEYCLOAK_CLIENT_ID` | `techdengue-frontend` | Client ID |

**Nota**: Ajuste as URLs conforme seu ambiente.

### 2.4 Deploy!

Clique em **Deploy site**.

Netlify vai:
1. ✅ Clone do repositório
2. ✅ Install dependencies (`npm ci`)
3. ✅ Run build (`npm run build`)
4. ✅ Publish `dist/` folder
5. ✅ Generate SSL certificate (HTTPS automático)

**Tempo estimado**: 2-3 minutos

---

## 🌐 Passo 3: Configurar Domínio (Opcional)

### 3.1 Domínio Netlify (Gratuito)

Netlify fornece automaticamente:
```
https://random-name-123456.netlify.app
```

**Customizar**:
1. **Site settings** → **Domain management**
2. **Options** → **Edit site name**
3. Digite: `techdengue-mt` (se disponível)
4. Resultado: `https://techdengue-mt.netlify.app`

### 3.2 Domínio Customizado

Se você tem `techdengue.mt.gov.br`:

1. **Add custom domain** → Digite `app.techdengue.mt.gov.br`
2. **Verify DNS configuration**
3. Adicione registro DNS no seu provedor:

```
Type: CNAME
Name: app
Value: techdengue-mt.netlify.app
```

4. **Verify DNS** no Netlify
5. ✅ SSL automático (Let's Encrypt)

---

## 🔄 Passo 4: CI/CD Automático

### 4.1 Deploy Automático

Já está configurado! A partir de agora:

**Push para `main`**:
```bash
git push origin main
```
→ Deploy automático em **Production**

**Push para `develop`**:
```bash
git push origin develop
```
→ Deploy automático em **Branch Deploy** (preview)

**Pull Request**:
→ Netlify cria **Deploy Preview** automático

### 4.2 Configurar GitHub Actions

O workflow `.github/workflows/frontend-ci.yml` já está criado e vai rodar automaticamente em cada push/PR:

**Jobs executados**:
1. ✅ **Lint** (ESLint)
2. ✅ **Type Check** (TypeScript)
3. ✅ **Build** (Vite)
4. ✅ **E2E Tests** (Playwright - apenas PRs)

**Ver resultados**:
- GitHub → **Actions** tab
- Cada commit terá ✅ ou ❌

### 4.3 Configurar Branch Deploy Contexts no Netlify

**Site settings** → **Build & deploy** → **Deploy contexts**:

- **Production branch**: `main`
- **Branch deploys**: `develop`
- **Deploy Previews**: `All pull requests`

---

## 🔒 Passo 5: Configurações de Segurança

### 5.1 Security Headers (já configurado)

O arquivo `netlify.toml` já inclui:
- ✅ `X-Content-Type-Options: nosniff`
- ✅ `X-Frame-Options: DENY`
- ✅ `X-XSS-Protection: 1; mode=block`
- ✅ `Referrer-Policy: strict-origin-when-cross-origin`

### 5.2 Cache Headers

Assets com hash são cached por 1 ano:
```
Cache-Control: public, max-age=31536000, immutable
```

Service Worker (`sw.js`) não é cached:
```
Cache-Control: no-cache, no-store, must-revalidate
```

### 5.3 HTTPS e HSTS

- ✅ HTTPS automático (Let's Encrypt)
- ✅ HTTP → HTTPS redirect automático
- ✅ HSTS header incluído

---

## 📊 Passo 6: Monitoramento e Logs

### 6.1 Netlify Analytics (Opcional - Pago)

**Site settings** → **Analytics**:
- Pageviews
- Unique visitors
- Top pages
- Referrers

### 6.2 Build Logs

**Deploys** → Selecione deploy → **Deploy log**

Ver:
- Install dependencies
- Build output
- Erros (se houver)

### 6.3 Function Logs (se usar)

**Functions** → **Function log**

---

## 🧪 Passo 7: Testar Deploy

### 7.1 Verificar Build

Acesse: `https://SEU_SITE.netlify.app`

**Checklist**:
- [ ] Página carrega
- [ ] Sem erros no console (F12)
- [ ] Autenticação funciona
- [ ] APIs conectam
- [ ] Mapa renderiza
- [ ] Dashboard carrega
- [ ] PWA installable

### 7.2 Testar PWA

**Chrome DevTools**:
1. F12 → **Application** tab
2. **Service Workers** → Deve aparecer
3. **Manifest** → Verificar `manifest.webmanifest`
4. **Storage** → IndexedDB deve estar disponível

**Lighthouse**:
1. F12 → **Lighthouse** tab
2. Selecione **Progressive Web App**
3. **Generate report**
4. Score deve ser > 90

### 7.3 Testar Offline

1. Abra site no Chrome
2. F12 → **Network** tab
3. Marque **Offline**
4. Recarregue página
5. ✅ Deve carregar do Service Worker

---

## 🔄 Workflow de Deploy

### Desenvolvimento

```bash
# 1. Criar feature branch
git checkout -b feature/nova-funcionalidade

# 2. Desenvolver
# ... code ...

# 3. Commit
git add .
git commit -m "feat: nova funcionalidade"

# 4. Push
git push origin feature/nova-funcionalidade

# 5. Abrir PR no GitHub
# → GitHub Actions roda CI
# → Netlify cria Deploy Preview

# 6. Review e merge
# → Merge para develop
# → Netlify deploya em branch deploy

# 7. Quando pronto para produção
git checkout main
git merge develop
git push origin main
# → Netlify deploya em production
```

---

## 📝 Comandos Úteis

### Build Local

```bash
cd frontend

# Install
npm install

# Dev mode
npm run dev

# Build
npm run build

# Preview build
npm run preview

# Lint
npm run lint

# Type check
npm run typecheck
```

### Deploy Manual (se necessário)

```bash
# Instalar Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy para preview
netlify deploy

# Deploy para production
netlify deploy --prod
```

---

## 🐛 Troubleshooting

### Build Falha no Netlify

**Erro**: `Module not found`
**Solução**: Verificar `package.json` e `package-lock.json` no Git

**Erro**: `Out of memory`
**Solução**: Adicionar env var `NODE_OPTIONS=--max_old_space_size=4096`

### Environment Variables Não Funcionam

**Problema**: `import.meta.env.VITE_API_URL` é `undefined`
**Solução**: 
1. Verificar se vars começam com `VITE_`
2. Rebuild após adicionar vars no Netlify
3. Verificar se vars estão em **Site settings** → **Environment variables**

### PWA Não Atualiza

**Problema**: Service Worker cached
**Solução**:
1. Incrementar `version` em `package.json`
2. Clear cache no navegador
3. Hard refresh (Ctrl+Shift+R)

### CORS Error

**Problema**: `CORS policy: No 'Access-Control-Allow-Origin'`
**Solução**: Configurar CORS no backend para incluir URL do Netlify

---

## 📊 Checklist Pré-Deploy

- [ ] .gitignore completo
- [ ] Environment variables configuradas
- [ ] netlify.toml presente
- [ ] Build local funciona (`npm run build`)
- [ ] TypeCheck passa (`npm run typecheck`)
- [ ] Lint passa (`npm run lint`)
- [ ] URLs de API corretas
- [ ] Keycloak configurado
- [ ] Service Worker testado
- [ ] GitHub Actions configurado
- [ ] Domínio configurado (se customizado)

---

## 🎯 URLs Importantes

**Netlify**:
- Dashboard: <https://app.netlify.com>
- Docs: <https://docs.netlify.com>
- Status: <https://www.netlifystatus.com/>

**GitHub**:
- Repository: `https://github.com/SEU_USUARIO/techdengue-mt`
- Actions: `https://github.com/SEU_USUARIO/techdengue-mt/actions`

**Seu Site**:
- Production: `https://techdengue-mt.netlify.app` (ou customizado)
- Develop: `https://develop--techdengue-mt.netlify.app`

---

## 📞 Suporte

**Problemas**:
1. Verificar **Netlify Deploy log**
2. Verificar **GitHub Actions**
3. Verificar **Browser Console** (F12)

**Documentação relacionada**:
- `docs/FRONTEND_PWA_README.md` - Frontend
- `docs/HARDENING_SECURITY_README.md` - Security
- `docs/TESTES_PERFORMANCE_README.md` - Tests

---

**Equipe TechDengue MT**  
**Data**: 2024-11-02  
**Versão**: 1.0.0

**Pronto para deploy!** 🚀
