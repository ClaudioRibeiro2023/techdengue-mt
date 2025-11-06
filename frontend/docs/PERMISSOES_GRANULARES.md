# 🔐 Sistema de Permissões Granulares

## 🎯 Visão Geral

Evolução do sistema de roles para **permissões específicas por ação e recurso**.

**Formato**: `RECURSO.ACAO` (ex: `DASHBOARD.VIEW`, `MAPA.EDIT`)

**Benefícios**:
- ✅ Controle fino de acesso
- ✅ Facilita auditoria
- ✅ Reduz necessidade de criar novas roles
- ✅ Composição flexível de permissões

---

## 📋 Estrutura de Permissões

### Ações Disponíveis

| Ação | Descrição | Exemplo |
|------|-----------|---------|
| `VIEW` | Visualizar recurso | Ver dashboard |
| `CREATE` | Criar novo registro | Criar formulário |
| `EDIT` | Editar registro existente | Editar parâmetro |
| `DELETE` | Deletar registro | Remover usuário |
| `EXECUTE` | Executar operação | Rodar simulação |
| `EXPORT` | Exportar dados | Download CSV |
| `ADMIN` | Administração completa | Todas as ações |

### Recursos Disponíveis

| Recurso | Descrição |
|---------|-----------|
| `DASHBOARD` | Dashboard executivo |
| `MAPA` | Mapa vivo |
| `PREVISAO` | Previsão & Simulação |
| `VIGILANCIA_ENTOMOLOGICA` | Vigilância entomológica |
| `VIGILANCIA_EPIDEMIOLOGICA` | Vigilância epidemiológica |
| `RESPOSTA_OPERACIONAL` | Resposta operacional |
| `RELATORIOS` | Relatórios |
| `ETL` | Integração ETL |
| `ADMIN` | Administração |
| `OBSERVABILIDADE` | Observabilidade |
| `DENUNCIA` | e-Denúncia |
| `USUARIOS` | Gestão de usuários |
| `PARAMETROS` | Parâmetros do sistema |
| `AUDITORIA` | Auditoria |

---

## 🔑 Mapeamento de Roles

### ADMIN

**Permissões**: Todas (100+ permissões)

**Acesso total** a todos os recursos e ações.

### GESTOR

**Permissões**: ~40 permissões

**Principais**:
- ✅ Visualização de tudo
- ✅ Exportação de relatórios
- ✅ Criação de resposta operacional
- ✅ Execução de previsões
- ✅ Auditoria (view + export)
- ❌ Administração de sistema
- ❌ Gestão de usuários (apenas view)

### VIGILANCIA

**Permissões**: ~20 permissões

**Principais**:
- ✅ CRUD completo de vigilância ento/epi
- ✅ Criação de resposta operacional
- ✅ Exportação de dados de vigilância
- ❌ Gestão de usuários
- ❌ Parâmetros do sistema
- ❌ ETL

### CAMPO

**Permissões**: ~10 permissões

**Principais**:
- ✅ Visualização básica de dashboard e mapa
- ✅ Criação de registros de vigilância
- ✅ Execução de resposta no campo
- ✅ Criação de denúncias
- ❌ Edição/deleção
- ❌ Relatórios
- ❌ Admin

---

## 🚀 Uso Prático

### 1. Hook usePermissions

```tsx
import { usePermissions } from '@/hooks/usePermissions'

function Dashboard() {
  const { hasPermission, can, getAccessLevel } = usePermissions()

  // Verificar permissão específica
  if (hasPermission('DASHBOARD.EXPORT')) {
    // Mostrar botão de export
  }

  // Verificar ação em recurso
  if (can('EDIT', 'MAPA')) {
    // Habilitar edição do mapa
  }

  // Obter nível de acesso
  const level = getAccessLevel('DASHBOARD')
  // level = 'ADMIN' | 'VIEW' | null
}
```

### 2. Componente PermissionGate

```tsx
import { PermissionGate } from '@/components/auth/PermissionGate'

function AdminPanel() {
  return (
    <PermissionGate permission="ADMIN.VIEW">
      <AdminContent />
    </PermissionGate>
  )
}
```

**Com fallback**:
```tsx
<PermissionGate 
  permission="DASHBOARD.EXPORT"
  fallback={<p>Você não pode exportar dados</p>}
>
  <ExportButton />
</PermissionGate>
```

**Múltiplas permissões**:
```tsx
<PermissionGate 
  permissions={['ADMIN.VIEW', 'ADMIN.EDIT']}
  requireAll={false} // pelo menos uma
>
  <AdminTools />
</PermissionGate>
```

### 3. Componente Can (Simplificado)

```tsx
import { Can } from '@/components/auth/PermissionGate'

function DataTable() {
  return (
    <div>
      <h1>Dados</h1>
      
      <Can action="CREATE" resource="VIGILANCIA_ENTOMOLOGICA">
        <button>Adicionar</button>
      </Can>
      
      <Can action="EDIT" resource="VIGILANCIA_ENTOMOLOGICA">
        <button>Editar</button>
      </Can>
      
      <Can action="DELETE" resource="VIGILANCIA_ENTOMOLOGICA">
        <button>Deletar</button>
      </Can>
    </div>
  )
}
```

### 4. Componente AccessLevel

```tsx
import { AccessLevel } from '@/components/auth/PermissionGate'

function Dashboard() {
  return (
    <AccessLevel resource="DASHBOARD">
      {(level) => (
        <>
          <h1>Dashboard</h1>
          
          {level === 'ADMIN' && <AdminControls />}
          {level === 'EXPORT' && <ExportButton />}
          {level === 'VIEW' && <ViewOnlyBadge />}
          {!level && <NoAccessMessage />}
        </>
      )}
    </AccessLevel>
  )
}
```

### 5. Componente AccessSwitch

```tsx
import { AccessSwitch } from '@/components/auth/PermissionGate'

function DashboardPage() {
  return (
    <AccessSwitch resource="DASHBOARD">
      <AccessSwitch.Admin>
        <AdminDashboard />
      </AccessSwitch.Admin>
      
      <AccessSwitch.Edit>
        <EditorDashboard />
      </AccessSwitch.Edit>
      
      <AccessSwitch.View>
        <ViewerDashboard />
      </AccessSwitch.View>
      
      <AccessSwitch.None>
        <NoAccessPage />
      </AccessSwitch.None>
    </AccessSwitch>
  )
}
```

---

## 📊 Exemplos Completos

### Exemplo 1: Tabela com CRUD Condicional

```tsx
import { Can } from '@/components/auth/PermissionGate'
import { usePermissions } from '@/hooks/usePermissions'

function UsersTable() {
  const { can } = usePermissions()

  return (
    <div>
      <div className="header">
        <h1>Usuários</h1>
        
        <Can action="CREATE" resource="USUARIOS">
          <button onClick={handleCreate}>
            Adicionar Usuário
          </button>
        </Can>
      </div>

      <table>
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Ações</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.name}</td>
              <td>{user.email}</td>
              <td>
                <Can action="EDIT" resource="USUARIOS">
                  <button onClick={() => handleEdit(user)}>
                    Editar
                  </button>
                </Can>
                
                <Can action="DELETE" resource="USUARIOS">
                  <button onClick={() => handleDelete(user)}>
                    Deletar
                  </button>
                </Can>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
```

### Exemplo 2: Formulário com Campos Condicionais

```tsx
import { PermissionGate } from '@/components/auth/PermissionGate'
import { usePermissions } from '@/hooks/usePermissions'

function ConfigForm() {
  const { can, hasAllPermissions } = usePermissions()

  return (
    <form>
      {/* Campos básicos (todos veem) */}
      <input name="title" />
      <input name="description" />

      {/* Campos avançados (apenas ADMIN) */}
      <PermissionGate permission="PARAMETROS.EDIT">
        <input name="threshold" type="number" />
        <input name="algorithm" />
      </PermissionGate>

      {/* Botão salvar (se pode editar) */}
      <Can action="EDIT" resource="PARAMETROS">
        <button type="submit">Salvar</button>
      </Can>
    </form>
  )
}
```

### Exemplo 3: Dashboard com Widgets Condicionais

```tsx
import { Can, PermissionGate } from '@/components/auth/PermissionGate'

function Dashboard() {
  return (
    <div className="dashboard">
      {/* Widget sempre visível */}
      <StatsWidget />

      {/* Widget de exportação */}
      <Can action="EXPORT" resource="DASHBOARD">
        <ExportWidget />
      </Can>

      {/* Widget de gestão (GESTOR ou ADMIN) */}
      <PermissionGate 
        permissions={[
          'RESPOSTA_OPERACIONAL.CREATE',
          'RESPOSTA_OPERACIONAL.EDIT'
        ]}
      >
        <ManagementWidget />
      </PermissionGate>

      {/* Widget de admin */}
      <Can action="ADMIN" resource="DASHBOARD">
        <AdminWidget />
      </Can>
    </div>
  )
}
```

### Exemplo 4: Menu Lateral Dinâmico

```tsx
import { Can } from '@/components/auth/PermissionGate'
import { usePermissions } from '@/hooks/usePermissions'

function Sidebar() {
  const { permissions } = usePermissions()

  return (
    <nav>
      {/* Sempre visível */}
      <MenuItem to="/dashboard" icon="BarChart">
        Dashboard
      </MenuItem>

      <Can action="VIEW" resource="MAPA">
        <MenuItem to="/mapa" icon="Map">
          Mapa Vivo
        </MenuItem>
      </Can>

      <Can action="VIEW" resource="VIGILANCIA_ENTOMOLOGICA">
        <MenuItem to="/vigilancia/ento" icon="Bug">
          Vigilância Entomológica
        </MenuItem>
      </Can>

      <Can action="VIEW" resource="RELATORIOS">
        <MenuItem to="/relatorios" icon="FileText">
          Relatórios
        </MenuItem>
      </Can>

      <Can action="ADMIN" resource="ADMIN">
        <MenuItem to="/admin" icon="Settings">
          Administração
        </MenuItem>
      </Can>

      {/* Debug: Mostrar permissões */}
      {import.meta.env.DEV && (
        <details>
          <summary>Minhas Permissões ({permissions.length})</summary>
          <ul>
            {permissions.map(p => (
              <li key={p}><code>{p}</code></li>
            ))}
          </ul>
        </details>
      )}
    </nav>
  )
}
```

---

## 🔄 Migração do Sistema Atual

### Antes (Roles Simples)

```tsx
import { useAuth } from '@/contexts/AuthContext'

function AdminPanel() {
  const { hasRole } = useAuth()

  if (!hasRole('ADMIN')) {
    return <AccessDenied />
  }

  return <AdminContent />
}
```

### Depois (Permissões Granulares)

```tsx
import { PermissionGate } from '@/components/auth/PermissionGate'

function AdminPanel() {
  return (
    <PermissionGate 
      permission="ADMIN.VIEW"
      fallback={<AccessDenied />}
    >
      <AdminContent />
    </PermissionGate>
  )
}
```

**Benefícios**:
- ✅ Mais claro qual ação está sendo verificada
- ✅ Fácil adicionar novas ações sem criar roles
- ✅ Código mais declarativo
- ✅ Logging automático de permissões

---

## 🧪 Testes

### Teste Unitário

```tsx
import { renderHook } from '@testing-library/react'
import { usePermissions } from '@/hooks/usePermissions'

describe('usePermissions', () => {
  it('ADMIN deve ter todas permissões', () => {
    // Mock user com role ADMIN
    const { result } = renderHook(() => usePermissions())
    
    expect(result.current.can('VIEW', 'DASHBOARD')).toBe(true)
    expect(result.current.can('EDIT', 'DASHBOARD')).toBe(true)
    expect(result.current.can('ADMIN', 'DASHBOARD')).toBe(true)
  })

  it('CAMPO deve ter apenas VIEW de dashboard', () => {
    // Mock user com role CAMPO
    const { result } = renderHook(() => usePermissions())
    
    expect(result.current.can('VIEW', 'DASHBOARD')).toBe(true)
    expect(result.current.can('EDIT', 'DASHBOARD')).toBe(false)
    expect(result.current.can('ADMIN', 'DASHBOARD')).toBe(false)
  })
})
```

### Teste E2E

```typescript
// e2e/permissions.spec.ts
import { test, expect } from '@playwright/test'

test.describe('Permissões Granulares', () => {
  test('GESTOR vê botão de export', async ({ page }) => {
    await page.goto('/?e2e-roles=GESTOR')
    await page.goto('/dashboard')
    
    // Deve ver botão de export
    await expect(page.getByRole('button', { name: /exportar/i })).toBeVisible()
    
    // Não deve ver botão de admin
    await expect(page.getByRole('button', { name: /configurações/i })).not.toBeVisible()
  })

  test('CAMPO não vê botão de export', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Não deve ver botão de export
    await expect(page.getByRole('button', { name: /exportar/i })).not.toBeVisible()
  })
})
```

---

## 📈 Matriz Completa de Permissões

### Dashboard

| Ação | ADMIN | GESTOR | VIGILANCIA | CAMPO |
|------|-------|--------|------------|-------|
| VIEW | ✅ | ✅ | ✅ | ✅ |
| EXPORT | ✅ | ✅ | ❌ | ❌ |
| ADMIN | ✅ | ❌ | ❌ | ❌ |

### Vigilância Entomológica

| Ação | ADMIN | GESTOR | VIGILANCIA | CAMPO |
|------|-------|--------|------------|-------|
| VIEW | ✅ | ✅ | ✅ | ✅ |
| CREATE | ✅ | ❌ | ✅ | ✅ |
| EDIT | ✅ | ❌ | ✅ | ❌ |
| DELETE | ✅ | ❌ | ❌ | ❌ |
| EXPORT | ✅ | ✅ | ✅ | ❌ |
| ADMIN | ✅ | ❌ | ❌ | ❌ |

### Usuários

| Ação | ADMIN | GESTOR | VIGILANCIA | CAMPO |
|------|-------|--------|------------|-------|
| VIEW | ✅ | ✅ | ❌ | ❌ |
| CREATE | ✅ | ❌ | ❌ | ❌ |
| EDIT | ✅ | ❌ | ❌ | ❌ |
| DELETE | ✅ | ❌ | ❌ | ❌ |

---

## 🎯 Boas Práticas

### ✅ DO

```tsx
// 1. Use Can para ações simples
<Can action="EDIT" resource="DASHBOARD">
  <EditButton />
</Can>

// 2. Use PermissionGate para blocos complexos
<PermissionGate permission="ADMIN.VIEW">
  <ComplexAdminPanel />
</PermissionGate>

// 3. Use AccessSwitch para UIs diferentes
<AccessSwitch resource="DASHBOARD">
  <AccessSwitch.Admin><AdminView /></AccessSwitch.Admin>
  <AccessSwitch.View><ReadView /></AccessSwitch.View>
</AccessSwitch>

// 4. Forneça fallback claro
<Can action="DELETE" resource="USUARIOS" fallback={<Tooltip>Sem permissão</Tooltip>}>
  <DeleteButton />
</Can>
```

### ❌ DON'T

```tsx
// 1. Não misture roles e permissões
if (hasRole('ADMIN') && hasPermission('DASHBOARD.VIEW')) { } // Confuso

// 2. Não verifique permissões manualmente
if (user.roles.includes('ADMIN')) { } // Use hooks/componentes

// 3. Não crie permissões muito específicas
'DASHBOARD.VIEW.WIDGET.1' // Muito granular!

// 4. Não duplique verificações
<PermissionGate permission="ADMIN.VIEW">
  {can('VIEW', 'ADMIN') && <Content />} // Redundante
</PermissionGate>
```

---

## 🔄 Próximos Passos

1. ✅ Sistema base implementado
2. ⏸️ Migrar componentes existentes
3. ⏸️ Adicionar testes E2E completos
4. ⏸️ Integrar com Keycloak (custom claims)
5. ⏸️ Dashboard visual de permissões
6. ⏸️ Auditoria de acessos negados

---

**Última atualização**: 06/11/2025  
**Versão**: 1.0.0
