# TechDengue Frontend

Frontend React do sistema TechDengue - Plataforma de Vigilância em Saúde para monitoramento e controle do Aedes aegypti.

## Stack Tecnológica

- **React 18** - UI Library
- **TypeScript** - Type Safety
- **Vite** - Build Tool & Dev Server
- **TailwindCSS** - Utility-First CSS
- **React Router v6** - Routing
- **OIDC Client TS** - Authentication (Keycloak)
- **Axios** - HTTP Client
- **React Query** - Server State Management
- **Leaflet** - Maps
- **Lucide React** - Icons
- **Vite PWA** - Progressive Web App

## Autenticação OIDC (Keycloak)

### Arquitetura

O sistema usa autenticação baseada em **OpenID Connect (OIDC)** com **Keycloak** como Identity Provider.

**Fluxo de Autenticação:**
1. Usuário acessa página protegida
2. Redirecionado para `/login`
3. Clicar em "Entrar" redireciona para Keycloak
4. Após login no Keycloak, retorna para `/auth/callback`
5. Token JWT é armazenado e usuário autenticado
6. Renovação automática de token (silent renew)

### Componentes de Autenticação

#### AuthContext (`src/contexts/AuthContext.tsx`)
Provider React que gerencia estado de autenticação:
- `user`: Dados do usuário (User do oidc-client-ts)
- `isAuthenticated`: Boolean indicando se usuário está autenticado
- `isLoading`: Boolean indicando carregamento inicial
- `login()`: Inicia fluxo de login
- `logout()`: Realiza logout
- `hasRole(role)`: Verifica se usuário tem role específica
- `hasAnyRole(roles[])`: Verifica se usuário tem alguma das roles
- `getAccessToken()`: Retorna access token atual

#### ProtectedRoute (`src/components/auth/ProtectedRoute.tsx`)
Componente wrapper para proteger rotas:
```tsx
// Proteger rota (qualquer usuário autenticado)
<ProtectedRoute>
  <HomePage />
</ProtectedRoute>

// Proteger rota (requer role específica)
<ProtectedRoute requiredRoles={['ADMIN', 'GESTOR']}>
  <ETLPage />
</ProtectedRoute>

// Proteger rota (requer TODAS as roles)
<ProtectedRoute requiredRoles={['ADMIN', 'GESTOR']} requireAllRoles>
  <AdminPage />
</ProtectedRoute>
```

#### useAuth Hook
Hook para acessar contexto de autenticação:
```tsx
import { useAuth } from '@/contexts/AuthContext'

function MyComponent() {
  const { user, isAuthenticated, login, logout, hasRole } = useAuth()
  
  if (hasRole('ADMIN')) {
    // Renderizar UI específica para admin
  }
}
```

### Páginas de Autenticação

- **LoginPage** (`src/pages/LoginPage.tsx`) - Página de login
- **CallbackPage** (`src/pages/auth/CallbackPage.tsx`) - Processa retorno do Keycloak
- **SilentRenewPage** (`src/pages/auth/SilentRenewPage.tsx`) - Renovação silenciosa de token

### Roles Disponíveis

Definidas em `src/config/auth.ts`:
- **ADMIN** - Acesso total ao sistema
- **GESTOR** - Gerenciamento e relatórios
- **VIGILANCIA** - Monitoramento epidemiológico
- **CAMPO** - Atividades de campo e registro

### Integração com APIs (Axios)

O arquivo `src/lib/api.ts` configura um cliente Axios com interceptors:

**Request Interceptor:**
- Adiciona automaticamente `Authorization: Bearer <token>` em todas as requisições

**Response Interceptor:**
- Detecta 401 (Unauthorized)
- Tenta renovar token automaticamente
- Redireciona para login se renovação falhar

Uso:
```tsx
import api from '@/lib/api'

// Requisição autenticada automaticamente
const response = await api.get('/v1/indicadores')
const data = await api.post('/v1/atividades', { ... })
```

### Componentes UI de Autenticação

#### UserMenu (`src/components/auth/UserMenu.tsx`)
Menu dropdown do usuário no header:
- Avatar com inicial do nome
- Nome e email
- Lista de roles
- Link para perfil
- Botão de logout

#### Header (`src/components/layout/Header.tsx`)
Header principal com:
- Logo e navegação
- UserMenu (quando autenticado)
- Botão "Entrar" (quando não autenticado)
- Menu mobile responsivo

## Configuração

### Variáveis de Ambiente

Copie `.env.example` para `.env` e ajuste:

```bash
# App
VITE_APP_URL=http://localhost:3000

# API URLs
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws

# Keycloak / OIDC
VITE_KEYCLOAK_URL=http://localhost:8080
VITE_KEYCLOAK_REALM=techdengue
VITE_KEYCLOAK_CLIENT_ID=techdengue-api

# Map
VITE_MAP_TOKEN=

# Tiles
VITE_TILES_BASE_URL=http://localhost:8080/tiles

# Feature Flags
VITE_FEATURE_TEMPORAL_WEEK=true
VITE_FEATURE_SOCIAL_LISTENING=false
VITE_FEATURE_DRONE_SIMULATOR=false
```

### Configuração OIDC

Arquivo: `src/config/auth.ts`

Customizar se necessário:
```typescript
export const oidcConfig: UserManagerSettings = {
  authority: `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}`,
  client_id: KEYCLOAK_CLIENT_ID,
  scope: 'openid profile email roles',
  // ... outras configurações
}
```

## Desenvolvimento

### Instalação

```bash
cd frontend
npm install
```

### Dev Server

```bash
npm run dev
```

Abre em http://localhost:3000

### Build

```bash
npm run build
```

Gera build otimizado em `dist/`

### Lint

```bash
npm run lint
```

### Type Check

```bash
npm run typecheck
```

## Estrutura de Diretórios

```
src/
├── components/
│   ├── auth/          # Componentes de autenticação
│   │   ├── ProtectedRoute.tsx
│   │   └── UserMenu.tsx
│   └── layout/        # Componentes de layout
│       ├── Header.tsx
│       └── MainLayout.tsx
├── config/
│   └── auth.ts        # Configuração OIDC
├── contexts/
│   └── AuthContext.tsx  # Context de autenticação
├── lib/
│   └── api.ts         # Cliente Axios configurado
├── pages/
│   ├── auth/
│   │   ├── CallbackPage.tsx
│   │   └── SilentRenewPage.tsx
│   ├── HomePage.tsx
│   ├── LoginPage.tsx
│   └── ProfilePage.tsx
├── App.tsx            # Rotas e setup principal
├── main.tsx           # Entry point
└── index.css          # Estilos globais (Tailwind)
```

## Rotas

### Públicas
- `/login` - Página de login
- `/auth/callback` - Callback do Keycloak
- `/auth/silent-renew` - Renovação silenciosa

### Protegidas (requer autenticação)
- `/` - Home/Dashboard
- `/profile` - Perfil do usuário
- `/mapa` - Mapa interativo
- `/dashboard` - Dashboard de indicadores
- `/relatorios` - Relatórios

### Protegidas (requer roles específicas)
- `/etl` - ETL de dados (ADMIN, GESTOR)

## Testando Autenticação

### 1. Iniciar Keycloak

```bash
cd infra
docker compose up -d keycloak
python keycloak/seed-keycloak.py
```

### 2. Iniciar Frontend

```bash
cd frontend
npm run dev
```

### 3. Testar Login

1. Acesse http://localhost:3000
2. Você será redirecionado para `/login`
3. Clique em "Entrar com Keycloak"
4. Faça login no Keycloak:
   - **Email:** admin@techdengue.com
   - **Senha:** admin123
5. Você será redirecionado de volta para a home

### 4. Verificar Autenticação

- Abra DevTools → Application → Local Storage
- Veja as chaves do OIDC (`oidc.user:...`)
- Verifique o token JWT armazenado

### 5. Testar Proteção de Rotas

- Tente acessar `/etl` com usuário sem role ADMIN/GESTOR
- Deve mostrar "Acesso Negado"

### 6. Testar Logout

- Clique no avatar no header
- Clique em "Sair"
- Você deve ser deslogado e redirecionado para Keycloak logout

## Troubleshooting

### "Redirect URI mismatch"
- Verifique se `http://localhost:3000/auth/callback` está configurado no Keycloak
- Client → techdengue-api → Valid Redirect URIs

### "CORS error"
- Verifique Web Origins no Keycloak client
- Adicione `http://localhost:3000`

### "Token expired"
- O sistema tenta renovar automaticamente
- Se falhar, usuário é redirecionado para login

### "Cannot find module oidc-client-ts"
- Execute `npm install`

### Silent renew não funciona
- Verifique se `/auth/silent-renew` está acessível
- Verifique `silent_redirect_uri` em `auth.ts`

## PWA (Progressive Web App)

Ícones PWA já estão gerados em `public/`:
- `pwa-192x192.png`
- `pwa-512x512.png`
- `manifest.webmanifest`

Para regenerar:
```bash
python scripts/generate-pwa-icons-simple.py
```

## Próximos Passos

- [ ] Implementar páginas reais (Mapa, Dashboard, ETL, Relatórios)
- [ ] Integrar Leaflet para mapas
- [ ] Configurar React Query para cache de dados
- [ ] Implementar WebSocket para atualizações em tempo real
- [ ] Adicionar testes (Vitest, React Testing Library)
- [ ] Implementar offline-first com PWA
- [ ] Adicionar notificações push

## Referências

- [OIDC Client TS Docs](https://github.com/authts/oidc-client-ts)
- [Keycloak Admin API](https://www.keycloak.org/docs/latest/server_admin/)
- [React Router v6](https://reactrouter.com/en/main)
- [Vite](https://vitejs.dev/)
- [TailwindCSS](https://tailwindcss.com/)
