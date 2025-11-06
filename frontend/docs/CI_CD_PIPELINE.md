# 🚀 CI/CD Pipeline - Frontend TechDengue

## 🎯 Visão Geral

Pipeline automatizado de Integração Contínua e Deploy Contínuo (CI/CD) usando GitHub Actions para garantir qualidade do código frontend.

---

## 📋 Workflows Configurados

### 1. Frontend CI (`frontend-ci.yml`)

**Trigger**:
- Push em `main` ou `develop`
- Pull requests para `main` ou `develop`
- Mudanças em `frontend/**`

**Jobs**:

| Job | Descrição | Quando Roda | Browsers |
|-----|-----------|-------------|----------|
| **lint-and-test** | Lint, typecheck, unit tests | Sempre | - |
| **build** | Build de produção | Sempre | - |
| **e2e-tests** | Testes E2E básicos | Sempre | Chromium |
| **e2e-tests-cross-browser** | Testes cross-browser | PRs e main | Firefox, Webkit |
| **e2e-tests-mobile** | Testes mobile | PRs e main | Mobile Chrome, Mobile Safari |

---

## 🔍 Detalhamento dos Jobs

### Job 1: Lint and Test

**Duração**: ~2 minutos

```yaml
steps:
  1. Checkout código
  2. Setup Node.js 18 com cache npm
  3. Instalar dependências (npm ci)
  4. Rodar linter (ESLint + Stylelint)
  5. Type check (TypeScript)
  6. Unit tests (se existirem)
```

**Artefatos**: Nenhum

**Falha se**:
- Erros de lint
- Erros de tipagem
- Unit tests falharem

---

### Job 2: Build

**Duração**: ~3 minutos  
**Dependência**: `lint-and-test`

```yaml
steps:
  1. Checkout código
  2. Setup Node.js 18 com cache npm
  3. Instalar dependências
  4. Build production (npm run build)
  5. Upload dist/ como artefato
```

**Artefatos**:
- `frontend-build` (7 dias retenção)

**Variáveis de ambiente**:
```yaml
VITE_API_URL: secrets.VITE_API_URL || 'http://localhost:8000/api'
VITE_KEYCLOAK_URL: secrets.VITE_KEYCLOAK_URL || 'http://localhost:8080'
VITE_KEYCLOAK_REALM: secrets.VITE_KEYCLOAK_REALM || 'techdengue'
VITE_KEYCLOAK_CLIENT_ID: secrets.VITE_KEYCLOAK_CLIENT_ID || 'techdengue-frontend'
```

**Falha se**:
- Build gerar erros
- Faltarem arquivos obrigatórios

---

### Job 3: E2E Tests (Chromium)

**Duração**: ~5 minutos  
**Dependência**: `lint-and-test`  
**Timeout**: 15 minutos

```yaml
steps:
  1. Checkout código
  2. Setup Node.js 18 com cache npm
  3. Instalar dependências
  4. Get Playwright version (para cache)
  5. Cache browsers Playwright
  6. Install Playwright (chromium, firefox, webkit) se não em cache
  7. Install system deps se em cache
  8. Rodar testes E2E (chromium) com 2 retries
  9. Upload relatórios (sempre)
  10. Upload screenshots/videos (se falhar)
```

**Artefatos**:
- `playwright-report-chromium` (14 dias)
- `playwright-failures-chromium` (7 dias - se falhar)

**Otimizações**:
- ✅ Cache de browsers do Playwright
- ✅ Retry automático (2x)
- ✅ Apenas Chromium (mais rápido)

**Falha se**:
- Testes falharem após 2 retries

---

### Job 4: E2E Tests (Cross-Browser)

**Duração**: ~10 minutos  
**Dependência**: `lint-and-test`  
**Timeout**: 20 minutos  
**Quando**: PRs ou push em `main`

```yaml
browsers:
  - Firefox
  - Webkit (Safari)
  
retries: 2 por browser
```

**Artefatos**:
- `playwright-report-cross-browser` (14 dias)
- `playwright-failures-cross-browser` (7 dias - se falhar)

**Por que separado?**
- Feedback mais rápido (Chromium primeiro)
- Roda apenas em PRs/main (economiza CI)
- Permite falha parcial sem bloquear

---

### Job 5: E2E Tests (Mobile)

**Duração**: ~8 minutos  
**Dependência**: `lint-and-test`  
**Timeout**: 20 minutos  
**Quando**: PRs ou push em `main`

```yaml
browsers:
  - Mobile Chrome (Pixel 5)
  - Mobile Safari (iPhone 12)
  
retries: 2 por browser
```

**Artefatos**:
- `playwright-report-mobile` (14 dias)
- `playwright-failures-mobile` (7 dias - se falhar)

**Testes validados**:
- Drawer navigation
- Focus trap
- Touch interactions
- Dark mode mobile

---

## 📊 Cobertura de Testes E2E

| Spec | Testes | Browsers | Descrição |
|------|--------|----------|-----------|
| `navigation.spec.ts` | 6+ | Todos | Menus, submenu, search, favorites |
| `roles.spec.ts` | 4+ | Todos | Visibilidade por roles |
| `collapse.spec.ts` | 2+ | Todos | Persistência de estado |
| `darkmode.spec.ts` | 1+ | Todos | Toggle dark mode |
| `mobile.spec.ts` | 6 | Mobile | Drawer, focus trap, Escape |
| `auth.spec.ts` | 5+ | Todos | Login, logout, token |
| `dashboard.spec.ts` | 8+ | Todos | KPIs, gráficos, performance |
| **TOTAL** | **76+** | **5** | - |

---

## ⚡ Performance e Otimizações

### Caching

```yaml
# Cache NPM packages
- uses: actions/setup-node@v4
  with:
    cache: 'npm'
    
# Cache Playwright browsers
- uses: actions/cache@v3
  with:
    path: ~/.cache/ms-playwright
    key: playwright-${{ runner.os }}-${{ playwright-version }}
```

**Benefícios**:
- 🚀 NPM install: ~2 min → ~30s
- 🚀 Playwright install: ~5 min → ~10s
- 💰 Economia de ~8 min por run

### Retries Automáticos

```yaml
run: npx playwright test --retries=2
```

**Benefícios**:
- 🛡️ Tolera flakiness ocasional
- 🎯 Reduz falsos positivos
- ⚠️ Ainda detecta bugs reais

### Paralelização

```yaml
jobs:
  lint-and-test: ...
  build: needs lint-and-test
  e2e-tests: needs lint-and-test
  e2e-tests-cross-browser: needs lint-and-test
  e2e-tests-mobile: needs lint-and-test
```

**Benefícios**:
- ⚡ 3 jobs E2E rodando em paralelo
- 📉 Tempo total: ~15 min (vs ~30 min sequencial)

---

## 🐛 Troubleshooting

### Testes E2E Falhando

**Passo 1: Ver artefatos**
1. GitHub Actions → Workflow run falhado
2. Artifacts → Download `playwright-report-*`
3. Abrir `index.html` localmente

**Passo 2: Ver screenshots/videos**
1. Artifacts → Download `playwright-failures-*`
2. Ver screenshots em `test-results/`
3. Ver vídeos (se habilitados)

**Passo 3: Reproduzir localmente**
```bash
npm run test:e2e -- e2e/<spec-que-falhou>.spec.ts --project=<browser>
```

### Cache Corrompido

**Limpar cache**:
```bash
# No GitHub: Settings → Actions → Caches → Delete cache
# Ou aguardar expiração (7 dias)
```

**Re-gerar cache**:
```bash
# Próximo run irá instalar do zero e criar novo cache
```

### Build Lento

**Otimizar dependências**:
```bash
# Analisar bundle
npm run build -- --analyze

# Remover dependencies não utilizadas
npm prune
```

---

## 🔐 Secrets Configurados

### GitHub Secrets Necessários

| Secret | Descrição | Obrigatório |
|--------|-----------|-------------|
| `VITE_API_URL` | URL do backend | Não (usa default) |
| `VITE_KEYCLOAK_URL` | URL do Keycloak | Não (usa default) |
| `VITE_KEYCLOAK_REALM` | Realm Keycloak | Não (usa default) |
| `VITE_KEYCLOAK_CLIENT_ID` | Client ID | Não (usa default) |

**Como configurar**:
1. GitHub repo → Settings → Secrets and variables → Actions
2. New repository secret
3. Adicionar chave e valor
4. Usar em workflow: `${{ secrets.SECRET_NAME }}`

---

## 📈 Métricas de Sucesso

### Targets

| Métrica | Target | Atual |
|---------|--------|-------|
| **Taxa de sucesso** | >95% | - |
| **Tempo total** | <20 min | ~15 min |
| **Flakiness** | <2% | - |
| **Cobertura E2E** | >70% | ~80% |

### Monitoramento

**Ver histórico**:
```
GitHub → Actions → frontend-ci → Runs
```

**Métricas úteis**:
- Tempo de execução por job
- Taxa de falha por spec
- Browsers mais problemáticos
- Flaky tests (falha inconsistente)

---

## 🔄 Workflows Futuros

### Planejados

**Deploy Automático (CD)**:
```yaml
deploy-staging:
  if: github.ref == 'refs/heads/develop'
  steps:
    - Deploy para staging
    - Smoke tests

deploy-production:
  if: github.ref == 'refs/heads/main'
  needs: [e2e-tests, e2e-tests-cross-browser, e2e-tests-mobile]
  steps:
    - Deploy para produção
    - Health checks
    - Notificação Slack
```

**Performance Monitoring**:
```yaml
lighthouse-ci:
  steps:
    - Lighthouse CI
    - Performance budget validation
    - Comentar métricas no PR
```

**Dependency Updates**:
```yaml
dependabot-auto-merge:
  if: github.actor == 'dependabot'
  steps:
    - Rodar testes
    - Auto-merge se passar
```

---

## 📚 Referências

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Playwright CI Docs](https://playwright.dev/docs/ci)
- [Actions Cache](https://github.com/actions/cache)
- [Upload Artifact](https://github.com/actions/upload-artifact)

---

## ✅ Checklist de Configuração

**Para novo repositório**:

- [ ] Copiar `.github/workflows/frontend-ci.yml`
- [ ] Configurar secrets (se necessário)
- [ ] Rodar primeiro workflow
- [ ] Verificar cache funcionando
- [ ] Validar relatórios gerados
- [ ] Configurar branch protection (require CI)
- [ ] Adicionar badge no README

**Badge para README**:
```markdown
![Frontend CI](https://github.com/seu-usuario/techdengue/actions/workflows/frontend-ci.yml/badge.svg)
```

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
