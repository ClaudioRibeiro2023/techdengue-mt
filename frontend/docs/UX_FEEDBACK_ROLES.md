# 🎨 Feedback Visual UX - Sistema de Roles

## 🎯 Visão Geral

Componentes visuais para melhorar a experiência do usuário ao interagir com o sistema de controle de acesso baseado em roles.

---

## 📦 Componentes Disponíveis

### 1. RoleBadge

Badge visual que mostra as roles do usuário autenticado.

**Localização**: `src/components/auth/RoleBadge.tsx`

**Uso**:
```tsx
import { RoleBadge } from '@/components/auth/RoleBadge'

// Modo compacto (mostra apenas a role mais alta)
<RoleBadge variant="compact" />

// Modo completo (mostra todas as roles)
<RoleBadge variant="full" showTooltip={true} />
```

**Props**:
- `variant`: `'compact'` | `'full'` (padrão: `'compact'`)
- `showTooltip`: boolean (padrão: `true`)

**Cores por Role**:
- **ADMIN**: 🟣 Roxo (Purple)
- **GESTOR**: 🔵 Azul (Blue)
- **VIGILANCIA**: 🟢 Verde (Green)
- **CAMPO**: 🟡 Âmbar (Amber)

**Integração**: Já integrado no Header principal.

---

### 2. RestrictedFeature

Wrapper para funcionalidades que requerem roles específicas.

**Localização**: `src/components/auth/RestrictedFeature.tsx`

**Uso Básico**:
```tsx
import { RestrictedFeature } from '@/components/auth/RestrictedFeature'

<RestrictedFeature requiredRoles={['ADMIN', 'GESTOR']}>
  <button onClick={handleDelete}>Deletar</button>
</RestrictedFeature>
```

**Com Lock Visual**:
```tsx
<RestrictedFeature 
  requiredRoles={['ADMIN']} 
  showLock={true}
  tooltipPosition="top"
>
  <button className="btn-primary">Ação Restrita</button>
</RestrictedFeature>
```

**Com Fallback Customizado**:
```tsx
<RestrictedFeature 
  requiredRoles={['ADMIN']} 
  fallback={<p className="text-gray-500">Somente Admin</p>}
>
  <button>Configurações Avançadas</button>
</RestrictedFeature>
```

**Props**:
- `requiredRoles`: `UserRole[]` - Roles necessárias
- `requireAllRoles`: boolean - Se true, exige todas as roles (default: false)
- `showLock`: boolean - Mostra ícone de cadeado (default: true)
- `fallback`: ReactNode - Componente alternativo quando sem acesso
- `tooltipPosition`: `'top'` | `'bottom'` | `'left'` | `'right'` (default: `'top'`)

---

### 3. Restricted (Componente Simples)

Versão simplificada para uso inline.

**Uso**:
```tsx
import { Restricted } from '@/components/auth/RestrictedFeature'

<div>
  <h1>Dashboard</h1>
  <Restricted roles={['ADMIN']}>
    <button>Configurações</button>
  </Restricted>
</div>
```

---

### 4. useRestricted (Hook)

Hook para verificar acesso programaticamente.

**Uso**:
```tsx
import { useRestricted } from '@/components/auth/RestrictedFeature'

function MyComponent() {
  const { hasAccess, missingRoles } = useRestricted(['ADMIN', 'GESTOR'])

  if (!hasAccess) {
    return <p>Você precisa de: {missingRoles.join(', ')}</p>
  }

  return <button onClick={handleAction}>Executar</button>
}
```

**Retorno**:
- `hasAccess`: boolean
- `missingRoles`: UserRole[]

---

### 5. AccessDeniedBanner

Banner informativo quando o usuário tenta acessar funcionalidade restrita.

**Localização**: `src/components/auth/AccessDeniedBanner.tsx`

**Uso**:
```tsx
import { AccessDeniedBanner } from '@/components/auth/AccessDeniedBanner'

<AccessDeniedBanner
  requiredRoles={['ADMIN']}
  currentPath="/admin/settings"
  variant="error"
  onDismiss={() => console.log('Banner fechado')}
/>
```

**Props**:
- `requiredRoles`: `UserRole[]`
- `currentPath`: string (opcional)
- `variant`: `'error'` | `'warning'` | `'info'` (default: `'warning'`)
- `onDismiss`: () => void (opcional)

**Variantes**:
- **error**: 🔴 Fundo vermelho (acesso negado crítico)
- **warning**: 🟡 Fundo âmbar (acesso limitado)
- **info**: 🔵 Fundo azul (informativo)

**Integração**: Usado automaticamente em `ProtectedRoute` quando falta role.

---

### 6. AccessDeniedInline

Versão compacta do banner para uso em espaços pequenos.

**Uso**:
```tsx
import { AccessDeniedInline } from '@/components/auth/AccessDeniedBanner'

<AccessDeniedInline roles={['ADMIN']} />
```

---

## 🎨 Exemplos Práticos

### Exemplo 1: Botão Administrativo

```tsx
import { RestrictedFeature } from '@/components/auth/RestrictedFeature'

function UserManagement() {
  return (
    <div>
      <h1>Gestão de Usuários</h1>
      
      <RestrictedFeature requiredRoles={['ADMIN']}>
        <button 
          onClick={handleAddUser}
          className="btn-primary"
        >
          Adicionar Usuário
        </button>
      </RestrictedFeature>
    </div>
  )
}
```

---

### Exemplo 2: Seção Condicional

```tsx
import { Restricted } from '@/components/auth/RestrictedFeature'

function Dashboard() {
  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* Visível para todos autenticados */}
      <section>
        <h2>Estatísticas Gerais</h2>
        <KPICards />
      </section>
      
      {/* Apenas para Admin e Gestor */}
      <Restricted roles={['ADMIN', 'GESTOR']}>
        <section>
          <h2>Relatórios Gerenciais</h2>
          <ManagementReports />
        </section>
      </Restricted>
      
      {/* Apenas para Admin */}
      <Restricted roles={['ADMIN']}>
        <section>
          <h2>Auditoria de Sistema</h2>
          <SystemAudit />
        </section>
      </Restricted>
    </div>
  )
}
```

---

### Exemplo 3: Verificação Programática

```tsx
import { useRestricted } from '@/components/auth/RestrictedFeature'

function DataExport() {
  const { hasAccess, missingRoles } = useRestricted(['ADMIN', 'GESTOR'], false)

  const handleExport = () => {
    if (!hasAccess) {
      alert(`Você precisa de: ${missingRoles.join(', ')}`)
      return
    }
    
    // Executar export
    exportData()
  }

  return (
    <button 
      onClick={handleExport}
      disabled={!hasAccess}
      className={!hasAccess ? 'btn-disabled' : 'btn-primary'}
    >
      Exportar Dados
    </button>
  )
}
```

---

### Exemplo 4: Card com Lock Visual

```tsx
import { RestrictedFeature } from '@/components/auth/RestrictedFeature'

function FeatureCard({ title, description, onClick, requiredRoles }) {
  return (
    <RestrictedFeature 
      requiredRoles={requiredRoles}
      showLock={true}
      tooltipPosition="bottom"
    >
      <div 
        onClick={onClick}
        className="card hover:shadow-lg cursor-pointer"
      >
        <h3>{title}</h3>
        <p>{description}</p>
      </div>
    </RestrictedFeature>
  )
}

// Uso
<FeatureCard
  title="Configurações Avançadas"
  description="Gerenciar parâmetros do sistema"
  onClick={handleSettings}
  requiredRoles={['ADMIN']}
/>
```

---

### Exemplo 5: Menu com Itens Restritos

```tsx
import { Restricted } from '@/components/auth/RestrictedFeature'

function Sidebar() {
  return (
    <nav>
      {/* Visível para todos */}
      <MenuItem to="/dashboard" icon="BarChart3">
        Dashboard
      </MenuItem>
      
      <MenuItem to="/mapa" icon="Map">
        Mapa Vivo
      </MenuItem>
      
      {/* Apenas Admin e Gestor */}
      <Restricted roles={['ADMIN', 'GESTOR']}>
        <MenuItem to="/relatorios" icon="FileText">
          Relatórios
        </MenuItem>
      </Restricted>
      
      {/* Apenas Admin */}
      <Restricted roles={['ADMIN']}>
        <MenuItem to="/admin" icon="Settings">
          Administração
        </MenuItem>
      </Restricted>
    </nav>
  )
}
```

---

## 🎭 Estados Visuais

### Estado Normal (Com Acesso)
```tsx
<RestrictedFeature requiredRoles={['ADMIN']}>
  <button className="btn-primary">Clique Aqui</button>
</RestrictedFeature>
```
**Renderiza**: Botão normal, totalmente funcional

---

### Estado Bloqueado (Sem Acesso)
```tsx
<RestrictedFeature requiredRoles={['ADMIN']} showLock={true}>
  <button className="btn-primary">Clique Aqui</button>
</RestrictedFeature>
```
**Renderiza**:
- Botão com opacity 50%
- Overlay semitransparente
- Ícone de cadeado 🔒
- Tooltip: "Requer: ADMIN"
- Cursor: not-allowed

---

### Estado Oculto (Sem Fallback)
```tsx
<RestrictedFeature requiredRoles={['ADMIN']} showLock={false}>
  <button className="btn-primary">Clique Aqui</button>
</RestrictedFeature>
```
**Renderiza**: Nada (componente não aparece)

---

## 🚀 Animações

Todas as animações estão definidas em `src/styles/navigation.css`:

```css
/* Slide down (usado em banners) */
.animate-slideDown {
  animation: slideDown 0.3s ease-out;
}

/* Fade in (usado em tooltips) */
.animate-fadeIn {
  animation: fadeIn 0.2s ease-out;
}

/* Pulse (usado em badges) */
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
```

---

## 🎯 Boas Práticas

### ✅ DO

```tsx
// 1. Use RestrictedFeature para UI components
<RestrictedFeature requiredRoles={['ADMIN']}>
  <button>Deletar</button>
</RestrictedFeature>

// 2. Use Restricted para blocos de conteúdo
<Restricted roles={['GESTOR']}>
  <section>Conteúdo gerencial</section>
</Restricted>

// 3. Use useRestricted para lógica
const { hasAccess } = useRestricted(['ADMIN'])
if (hasAccess) {
  performAdminAction()
}

// 4. Mostre feedback claro
<RestrictedFeature 
  requiredRoles={['ADMIN']}
  showLock={true}
  tooltipPosition="top"
>
  <ActionButton />
</RestrictedFeature>
```

### ❌ DON'T

```tsx
// 1. Não use diretamente hasRole para UI
const { hasRole } = useAuth()
{hasRole('ADMIN') && <button>Deletar</button>}
// Melhor: use Restricted

// 2. Não deixe UI sem feedback
{hasRole('ADMIN') ? <Button /> : null}
// Melhor: use RestrictedFeature com showLock=true

// 3. Não duplique verificações
if (hasRole('ADMIN')) {
  return <ProtectedRoute requiredRoles={['ADMIN']}>...</ProtectedRoute>
}
// ProtectedRoute já faz a verificação
```

---

## 📊 Integração com ProtectedRoute

O `ProtectedRoute` já usa `AccessDeniedBanner` automaticamente:

```tsx
// App.tsx
<Route 
  path="/admin" 
  element={
    <ProtectedRoute requiredRoles={['ADMIN']}>
      <AdminPage />
    </ProtectedRoute>
  } 
/>
```

Se o usuário não tiver a role ADMIN, verá:
- 🔴 Banner de erro
- Mensagem clara
- Roles necessárias listadas
- Path tentado
- Botões "Voltar" e "Ir para Home"

---

## 🧪 Testando

### Modo E2E (Bypass de Roles)

```bash
# .env.e2e
MODE=e2e
```

```tsx
// E2E test
await page.evaluate(() => {
  localStorage.setItem('e2e-roles', JSON.stringify(['CAMPO']))
})

await page.goto('/admin')
// Deve ver AccessDeniedBanner
```

### Modo DEMO (Todas as Roles)

```bash
# .env
VITE_DEMO_MODE=true
```

Usuário sempre tem todas as roles.

---

## 📈 Métricas

Com logging habilitado, todos os acessos são monitorados:

```typescript
// Logger automático em RestrictedFeature
logger.roleCheck('deny', 'ADMIN', { 
  reason: 'insufficient roles',
  component: 'RestrictedFeature'
})
```

Ver logs:
```javascript
// Console DevTools
const logs = JSON.parse(localStorage.getItem('error-logs') || '[]')
console.table(logs)
```

---

## 🔄 Migração de Código Legado

### Antes

```tsx
const { hasRole } = useAuth()

{hasRole('ADMIN') && (
  <button onClick={handleDelete}>Deletar</button>
)}
```

### Depois

```tsx
import { RestrictedFeature } from '@/components/auth/RestrictedFeature'

<RestrictedFeature requiredRoles={['ADMIN']}>
  <button onClick={handleDelete}>Deletar</button>
</RestrictedFeature>
```

**Benefícios**:
- ✅ Feedback visual automático
- ✅ Tooltip explicativo
- ✅ Logging automático
- ✅ Consistência visual

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
