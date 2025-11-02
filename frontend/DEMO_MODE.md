# 🎭 Modo Demo - TechDengue MT

## 📋 Visão Geral

O sistema suporta **dois modos de operação**:

- **Modo Produção** (com autenticação Keycloak)
- **Modo Demo** (sem autenticação, acesso direto)

A alternância entre modos é feita **apenas com variáveis de ambiente**, sem necessidade de alterar código.

---

## 🔧 Como Funciona

### Modo Produção (Padrão)

**Configuração**: Sem `VITE_DEMO_MODE` ou `VITE_DEMO_MODE=false`

**Comportamento**:
- ✅ Requer autenticação Keycloak
- ✅ Login via `/login`
- ✅ Proteção de rotas com `ProtectedRoute`
- ✅ Controle de acesso por roles (ADMIN, GESTOR, etc.)
- ✅ Redirecionamento automático para login se não autenticado

### Modo Demo

**Configuração**: `VITE_DEMO_MODE=true`

**Comportamento**:
- ✅ Acesso direto sem login
- ✅ Todas as rotas acessíveis
- ✅ Sem verificação de roles
- ✅ Rotas de autenticação desabilitadas (`/login`, `/auth/callback`)
- ✅ Ideal para demonstração e testes

---

## ⚙️ Configuração

### Local (Desenvolvimento)

Crie ou edite `.env.local`:

```bash
# Modo Demo
VITE_DEMO_MODE=true

# APIs (opcional)
VITE_API_URL=http://localhost:8000/api
```

### Netlify (Deploy)

**Opção 1: Site Settings → Environment Variables**

1. Acesse: https://app.netlify.com/
2. Selecione seu site
3. **Site settings** → **Environment variables**
4. Adicione/edite:
   - `VITE_DEMO_MODE` = `true`

**Opção 2: netlify.toml**

```toml
[context.production.environment]
  VITE_DEMO_MODE = "true"

[context.deploy-preview.environment]
  VITE_DEMO_MODE = "true"
```

### GitHub Actions

Edite `.github/workflows/frontend-ci.yml`:

```yaml
env:
  VITE_DEMO_MODE: true
  VITE_API_URL: http://localhost:8000/api
```

---

## 🔄 Alternando Entre Modos

### Para Modo Demo → Produção

**Netlify**:
1. **Site settings** → **Environment variables**
2. **Deletar** variável `VITE_DEMO_MODE` (ou mudar para `false`)
3. **Adicionar** variáveis Keycloak:
   ```
   VITE_KEYCLOAK_URL=https://keycloak.techdengue.mt.gov.br
   VITE_KEYCLOAK_REALM=techdengue
   VITE_KEYCLOAK_CLIENT_ID=techdengue-frontend
   ```
4. **Trigger deploy** → **Deploy site**

**Local**:
```bash
# .env.local
VITE_DEMO_MODE=false
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=techdengue
VITE_KEYCLOAK_CLIENT_ID=techdengue-frontend
```

### Para Produção → Modo Demo

**Netlify**:
1. **Site settings** → **Environment variables**
2. **Adicionar**: `VITE_DEMO_MODE` = `true`
3. **Deletar** (opcional): variáveis Keycloak
4. **Trigger deploy** → **Deploy site**

**Local**:
```bash
# .env.local
VITE_DEMO_MODE=true
```

---

## 🧪 Testando Localmente

### Modo Demo
```bash
cd frontend

# Criar .env.local
echo "VITE_DEMO_MODE=true" > .env.local

# Rodar
npm run dev

# Acessar
http://localhost:5173
# ✅ Acesso direto, sem login
```

### Modo Produção (com Keycloak local)
```bash
# .env.local
VITE_DEMO_MODE=false
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=techdengue
VITE_KEYCLOAK_CLIENT_ID=techdengue-frontend

# Rodar Keycloak (docker)
cd ../infra
docker-compose up keycloak

# Rodar frontend
cd ../frontend
npm run dev

# Acessar
http://localhost:5173
# → Redireciona para /login → Keycloak
```

---

## 📊 Diferenças Técnicas

| Aspecto | Modo Produção | Modo Demo |
|---------|---------------|-----------|
| **Autenticação** | Keycloak OIDC | Nenhuma |
| **AuthContext** | Carrega user real | User = null |
| **ProtectedRoute** | Bloqueia acesso | Permite todos |
| **Roles** | Verificados | Ignorados |
| **Login Page** | Ativo | Desabilitado |
| **Callback** | Processa OAuth | Desabilitado |

---

## 🔍 Implementação (Código)

### App.tsx

```typescript
const DEMO_MODE = import.meta.env.VITE_DEMO_MODE === 'true'

const RouteWrapper = ({ children }) => {
  return DEMO_MODE 
    ? <>{children}</> 
    : <ProtectedRoute>{children}</ProtectedRoute>
}

// Rotas de auth desabilitadas em demo
{!DEMO_MODE && (
  <>
    <Route path="/login" element={<LoginPage />} />
    <Route path="/auth/callback" element={<CallbackPage />} />
  </>
)}
```

### Verificação em Componentes

```typescript
import React from 'react'

const MyComponent = () => {
  const isDemoMode = import.meta.env.VITE_DEMO_MODE === 'true'
  
  return (
    <div>
      {isDemoMode && (
        <div className="bg-yellow-50 p-4">
          ⚠️ Modo Demo Ativo - Dados são fictícios
        </div>
      )}
      {/* resto do componente */}
    </div>
  )
}
```

---

## ⚠️ Avisos Importantes

### Segurança

- **Modo Demo NÃO deve ser usado em produção real** com dados sensíveis
- Sem autenticação = qualquer pessoa pode acessar
- Ideal apenas para demonstrações e ambientes de teste

### Performance

- Modo Demo não afeta performance
- Bundle size é o mesmo (code splitting remove código não usado)

### Backend

- Modo Demo só afeta o **frontend**
- Backend ainda requer autenticação nas APIs
- Configure CORS para permitir origin do Netlify

---

## 🎯 Casos de Uso

### ✅ Quando Usar Modo Demo

- Demonstrações para stakeholders
- Testes de interface (sem backend)
- Deploy preview no Netlify
- Desenvolvimento rápido de UI
- Treinamento de usuários

### ❌ Quando NÃO Usar Modo Demo

- Produção com dados reais
- Ambientes com requisitos de auditoria
- Sistemas com dados sensíveis/LGPD
- Quando controle de acesso é obrigatório

---

## 📝 Checklist de Deploy

### Deploy Modo Demo
- [ ] `VITE_DEMO_MODE=true` configurado no Netlify
- [ ] Build bem-sucedido
- [ ] Acesso direto ao site funciona
- [ ] Todas as rotas acessíveis

### Deploy Modo Produção
- [ ] `VITE_DEMO_MODE` removido ou `=false`
- [ ] Variáveis Keycloak configuradas
- [ ] Keycloak acessível publicamente
- [ ] Callback URL configurado no Keycloak
- [ ] Login funciona corretamente
- [ ] Proteção de rotas ativa

---

## 🔗 Referências

- **Configuração Keycloak**: `infra/keycloak/README.md`
- **Deploy Guide**: `docs/DEPLOY_GUIDE.md`
- **Frontend README**: `frontend/README.md`

---

**Versão**: 1.0.0  
**Data**: 2024-11-02  
**Modo Atual no Netlify**: Demo ✅
