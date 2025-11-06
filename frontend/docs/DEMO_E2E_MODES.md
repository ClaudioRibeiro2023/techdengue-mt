# 🛠️ DEMO e E2E Modes - TechDengue

## 📋 Sumário
- [Visão Geral](#visão-geral)
- [DEMO Mode](#demo-mode)
- [E2E Mode](#e2e-mode)
- [Configuração](#configuração)
- [Quando Usar Cada Modo](#quando-usar-cada-modo)
- [Migração de Flags Antigas](#migração-de-flags-antigas)

---

## Visão Geral

O TechDengue possui **dois modos especiais** para desenvolvimento e testes:

| Modo | Propósito | Autenticação | Roles |
|------|-----------|-------------|-------|
| **DEMO** | Demonstração sem backend | ❌ Desabilitada | ✅ Todas |
| **E2E** | Testes automatizados | ❌ Desabilitada | ⚙️ Simuladas |

---

## DEMO Mode

### 🎯 Para Que Serve

- **Demonstrações** sem necessidade de backend/Keycloak rodando
- **Desenvolvimento de UI** sem depender de serviços externos
- **Apresentações** para stakeholders

### ⚙️ Como Ativar

**Variável de ambiente**:
```bash
VITE_DEMO_MODE=true
```

**Arquivo `.env.demo`**:
```env
VITE_DEMO_MODE=true
VITE_API_BASE_URL=http://localhost:8000
```

**Rodar**:
```bash
npm run dev -- --mode demo
```

### ✨ Comportamento

1. **Autenticação desabilitada**
   - Não redireciona para `/login`
   - Não valida JWT tokens
   - Usuário sempre autenticado

2. **Todas as roles disponíveis**
   ```typescript
   hasRole('ADMIN')      // ✅ true
   hasRole('GESTOR')     // ✅ true
   hasRole('VIGILANCIA') // ✅ true
   hasRole('CAMPO')      // ✅ true
   ```

3. **Todos os menus visíveis**
   - Dashboard Executivo
   - Mapa Vivo
   - Previsão & Simulação
   - Vigilância Epi/Ento
   - Resposta Operacional
   - Administração
   - Observabilidade

4. **Mock de dados** (se implementado)
   - Dados fictícios para demonstração
   - Não consome API real

### 🚨 Restrições

- **NÃO usar em produção**
- **NÃO fazer deploy** com `DEMO_MODE=true`
- **NÃO expor** publicamente

---

## E2E Mode

### 🎯 Para Que Serve

- **Testes automatizados** com Playwright
- **Validação de navegação** e interações
- **CI/CD pipelines**

### ⚙️ Como Ativar

**Configuração Playwright**:
```typescript
// playwright.config.ts
webServer: {
  command: 'npm run dev -- --mode e2e --port 6090',
  url: 'http://localhost:6090'
}
```

**Rodar manualmente**:
```bash
vite --mode e2e --port 6090
```

**Executar testes**:
```bash
npm run test:e2e
```

### ✨ Comportamento

1. **Autenticação desabilitada**
   - Igual ao DEMO mode
   - Não valida Keycloak

2. **Roles simuladas via localStorage ou query**

   **Via localStorage**:
   ```typescript
   localStorage.setItem('e2e-roles', 'ADMIN,GESTOR')
   ```

   **Via URL query**:
   ```
   http://localhost:6090/modulos/dashboard?e2e=1&roles=VIGILANCIA,CAMPO
   ```

3. **Validação de UI e navegação**
   - Testes de menus
   - Testes de roles
   - Testes mobile (drawer, focus trap)
   - Testes dark mode

### 🧪 Exemplo de Teste

```typescript
// e2e/roles.spec.ts
test('admin vê todos os menus', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('e2e-roles', 'ADMIN')
  })
  await page.goto('/?e2e=1')
  
  // Verifica menu Admin visível
  await expect(page.locator('#app-sidebar').getByText('Administração')).toBeVisible()
})

test('campo não vê menu admin', async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem('e2e-roles', 'CAMPO')
  })
  await page.goto('/?e2e=1')
  
  // Administração não deve aparecer
  await expect(page.locator('#app-sidebar').getByText('Administração')).not.toBeVisible()
})
```

### 📊 Testes Existentes

| Spec | Cobertura |
|------|-----------|
| `navigation.spec.ts` | Menus, submenu, search, favorites, collapse |
| `roles.spec.ts` | Visibilidade por roles (ADMIN, GESTOR, VIGILANCIA, CAMPO) |
| `collapse.spec.ts` | Persistência de collapse (sidebar, submenu) |
| `darkmode.spec.ts` | Toggle dark mode |
| `mobile.spec.ts` | Drawer mobile, focus trap, Escape, overlay |

---

## Configuração

### Arquivos de Ambiente

```bash
frontend/
├── .env                 # Produção (VITE_DEMO_MODE=false)
├── .env.development     # Dev local (VITE_DEMO_MODE=false)
├── .env.demo            # Demo mode (VITE_DEMO_MODE=true)
└── .env.e2e             # E2E tests (VITE_DEMO_MODE=true, porta 6090)
```

### `.env` (Produção)
```env
VITE_DEMO_MODE=false
VITE_API_BASE_URL=http://localhost:8000
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=techdengue
VITE_KEYCLOAK_CLIENT_ID=techdengue-api
```

### `.env.demo`
```env
VITE_DEMO_MODE=true
VITE_API_BASE_URL=http://localhost:8000
```

### `.env.e2e`
```env
VITE_DEMO_MODE=true
VITE_API_BASE_URL=http://localhost:6090
```

---

## Quando Usar Cada Modo

### ✅ Use DEMO Mode

- Apresentando funcionalidades para stakeholders
- Desenvolvendo UI sem backend disponível
- Mostrando fluxos sem dados reais
- Treinamento de usuários

### ✅ Use E2E Mode

- Rodando testes Playwright
- Validando navegação automaticamente
- CI/CD pipelines
- Teste de regressão

### ✅ Use Modo Normal (Produção)

- Desenvolvimento com backend rodando
- Testes manuais com dados reais
- Ambientes staging/production
- Validação com autenticação real

---

## Migração de Flags Antigas

### ❌ Flags Removidas

Anteriormente usávamos `localStorage.getItem('bypass-auth')` para bypass manual. **Isso foi removido** para evitar bypass acidental em produção.

### Antes (DEPRECATED)
```typescript
// NÃO USE MAIS
localStorage.setItem('bypass-auth', '1')
```

### Agora (CORRETO)
```bash
# DEMO mode via env
npm run dev -- --mode demo

# E2E mode via Playwright
npm run test:e2e
```

### Código Atualizado

**App.tsx** (limpo):
```typescript
// Wrapper component for demo mode and E2E tests
const RouteWrapper = ({ children }: { children: React.ReactNode }) => {
  const MODE = import.meta.env.MODE
  return (DEMO_MODE || MODE === 'e2e') ? <>{children}</> : <ProtectedRoute>{children}</ProtectedRoute>
}
```

**ProtectedRoute.tsx** (limpo):
```typescript
if (DEMO_MODE || MODE === 'e2e') {
  return <>{children}</>
}
```

**AuthContext.tsx** (limpo):
```typescript
export function AuthProvider({ children }: { children: ReactNode }) {
  const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'
  const MODE = import.meta.env.MODE
  const OVERRIDE = DEMO_MODE || MODE === 'e2e'
  return OVERRIDE ? <BypassAuthProvider>{children}</BypassAuthProvider> : <RealAuthProvider>{children}</RealAuthProvider>
}
```

---

## Verificação Rápida

### Como saber qual modo está ativo?

**Console do navegador**:
```javascript
console.log('MODE:', import.meta.env.MODE)              // 'development' | 'demo' | 'e2e' | 'production'
console.log('DEMO_MODE:', import.meta.env.VITE_DEMO_MODE) // 'true' | 'false'
```

**DevTools React**:
```
<AuthContext.Provider value={{...}}>
  isAuthenticated: true (se DEMO/E2E)
  user: null (se DEMO/E2E)
</AuthContext.Provider>
```

---

## 🔒 Segurança

### Checklist de Deploy

- [ ] `.env` com `VITE_DEMO_MODE=false`
- [ ] Build com modo production (`npm run build`)
- [ ] Sem flags de bypass no localStorage
- [ ] Keycloak configurado corretamente
- [ ] Redirect URIs válidos
- [ ] Environment variables corretas

### Validação

```bash
# Verificar se não está em DEMO mode
grep VITE_DEMO_MODE .env
# Deve mostrar: VITE_DEMO_MODE=false

# Verificar build
npm run build
# Não deve haver warnings sobre DEMO mode
```

---

## 📚 Referências

- **ROLES_E_ACESSO.md** - Controle de acesso e Keycloak
- **KEYCLOAK_SETUP_RAPIDO.md** - Setup rápido de autenticação
- **Playwright Config** - `playwright.config.ts`
- **Vite Config** - `vite.config.ts`

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
