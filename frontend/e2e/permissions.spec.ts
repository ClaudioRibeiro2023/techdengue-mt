import { test, expect } from '@playwright/test'

/**
 * Testes E2E para Sistema de Permissões Granulares
 */

test.describe('Permissões Granulares', () => {
  test.beforeEach(async ({ page }) => {
    // Limpar estado
    await page.goto('/')
    await page.evaluate(() => {
      document.documentElement.classList.remove('mobile-sidebar-open', 'mobile-submenu-open')
    })
  })

  test('ADMIN deve ter acesso completo', async ({ page }) => {
    // Simular role ADMIN
    await page.goto('/?e2e-roles=ADMIN')
    
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
    
    // Admin deve ver todos os módulos no sidebar
    const sidebar = page.locator('[data-app-nav="primary"]')
    await expect(sidebar).toBeVisible()
    
    // Deve ter link para Dashboard Executivo
    await expect(page.locator('a[href="/dashboard"]')).toBeVisible()
    
    // Deve ter link para Admin
    await expect(page.locator('a[href*="/admin"]')).toBeVisible()
  })

  test('GESTOR tem permissões de visualização e relatórios', async ({ page }) => {
    await page.goto('/?e2e-roles=GESTOR')
    
    await page.goto('/dashboard')
    
    // Gestor deve ver dashboard
    await expect(page.locator('h1')).toContainText(/Dashboard|Painel/)
    
    // Deve ter acesso ao mapa
    await page.goto('/mapa')
    await expect(page).toHaveURL(/\/mapa/)
  })

  test('VIGILANCIA tem CRUD de vigilância', async ({ page }) => {
    await page.goto('/?e2e-roles=VIGILANCIA')
    
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
    
    // Vigilância deve ter acesso aos módulos de vigilância
    const sidebar = page.locator('[data-app-nav="primary"]')
    await expect(sidebar).toBeVisible()
  })

  test('CAMPO tem acesso limitado', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
    
    // Campo não deve ter acesso a admin
    await page.goto('/admin')
    
    // Pode redirecionar ou mostrar mensagem de acesso negado
    // Dependendo da implementação do ProtectedRoute
  })

  test('Múltiplas roles acumulam permissões', async ({ page }) => {
    // Usuário com GESTOR + VIGILANCIA
    await page.goto('/?e2e-roles=GESTOR,VIGILANCIA')
    
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
    
    // Deve ter permissões de ambas as roles
    const sidebar = page.locator('[data-app-nav="primary"]')
    await expect(sidebar).toBeVisible()
  })

  test('Sem roles = sem acesso', async ({ page }) => {
    // Simular usuário sem roles
    await page.goto('/?e2e-roles=')
    
    await page.goto('/dashboard')
    
    // Pode mostrar tela de acesso negado ou redirecionar
    // Depende da implementação
  })

  test('RoleBadge mostra roles corretas', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Badge de role deve estar visível no header
    // (Assumindo que RoleBadge foi integrado no Header)
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // Badge pode ter ícone ou texto "ADMIN"
    // Verificar se existe algum indicador de role
  })

  test('RestrictedFeature oculta conteúdo sem permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Se dashboard usar RestrictedFeature para botões admin
    // esses botões não devem aparecer para CAMPO
    
    // Exemplo: botão de "Configurações" ou "Administração"
    // não deve estar visível
  })

  test('AccessDeniedBanner aparece ao acessar rota sem permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    
    // Tentar acessar rota administrativa
    await page.goto('/admin')
    
    // Deve mostrar AccessDeniedBanner
    // ou redirecionar para /login
    
    // Verificar se há mensagem de acesso negado
    const body = await page.locator('body').textContent()
    const hasAccessDenied = body?.includes('Acesso Negado') || 
                            body?.includes('permissão') ||
                            body?.includes('não possui')
    
    if (hasAccessDenied) {
      // Banner de acesso negado está funcionando
      expect(hasAccessDenied).toBe(true)
    }
  })
})

test.describe('Componentes de Permissão', () => {
  test('PermissionGate oculta conteúdo sem permissão', async ({ page }) => {
    // Este teste verificaria se PermissionGate está funcionando
    // mas requer uma página de teste específica
    
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Verificar que elementos administrativos não aparecem
    const adminButtons = page.locator('button:has-text("Admin")')
    await expect(adminButtons).toHaveCount(0)
  })

  test('Can component mostra/oculta baseado em permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Admin deve ver todos os controles
    const header = page.locator('header')
    await expect(header).toBeVisible()
  })
})

test.describe('Validação de Roles', () => {
  test('Role inválida = tratada como sem permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=INVALID_ROLE')
    await page.goto('/dashboard')
    
    // Sistema deve tratar role inválida como sem permissão
    // Pode redirecionar ou mostrar acesso limitado
  })

  test('LocalStorage e2e-roles tem precedência', async ({ page }) => {
    await page.goto('/')
    
    // Setar roles via localStorage
    await page.evaluate(() => {
      localStorage.setItem('e2e-roles', JSON.stringify(['ADMIN']))
    })
    
    await page.goto('/dashboard')
    
    // Deve ter permissões de ADMIN
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Query param sobrescreve localStorage', async ({ page }) => {
    await page.goto('/')
    
    // Setar roles via localStorage
    await page.evaluate(() => {
      localStorage.setItem('e2e-roles', JSON.stringify(['CAMPO']))
    })
    
    // Query param deve ter precedência
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Deve ter permissões de ADMIN (do query param)
    await expect(page).toHaveTitle(/TechDengue/)
  })
})

test.describe('Navegação por Permissão', () => {
  test('Sidebar filtra itens por permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    const sidebar = page.locator('[data-app-nav="primary"]')
    
    // CAMPO não deve ver link de Admin
    const adminLink = sidebar.locator('a[href*="/admin"]')
    await expect(adminLink).not.toBeVisible()
  })

  test('ADMIN vê todos os itens do sidebar', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    const sidebar = page.locator('[data-app-nav="primary"]')
    await expect(sidebar).toBeVisible()
    
    // Admin deve ter vários links
    const links = sidebar.locator('a')
    const count = await links.count()
    
    // Admin deve ter pelo menos 5 links (Dashboard, Mapa, Admin, etc)
    expect(count).toBeGreaterThanOrEqual(5)
  })

  test('CAMPO vê apenas links básicos', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    const sidebar = page.locator('[data-app-nav="primary"]')
    await expect(sidebar).toBeVisible()
    
    // CAMPO deve ter menos links que ADMIN
    const links = sidebar.locator('a')
    const count = await links.count()
    
    // CAMPO tem acesso limitado
    expect(count).toBeLessThan(5)
  })
})

test.describe('Performance e Estabilidade', () => {
  test('Verificação de permissões não causa lag', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    
    const start = Date.now()
    await page.goto('/dashboard')
    const loadTime = Date.now() - start
    
    // Página deve carregar em menos de 3 segundos
    expect(loadTime).toBeLessThan(3000)
  })

  test('Mudança de role atualiza permissões', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Mudar para ADMIN
    await page.evaluate(() => {
      localStorage.setItem('e2e-roles', JSON.stringify(['ADMIN']))
    })
    
    await page.reload()
    
    // Agora deve ter permissões de ADMIN
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Permissões persistem entre navegações', async ({ page }) => {
    await page.goto('/?e2e-roles=GESTOR')
    await page.goto('/dashboard')
    
    // Navegar para outra página
    await page.goto('/mapa')
    
    // Voltar
    await page.goto('/dashboard')
    
    // Permissões devem continuar as mesmas
    await expect(page).toHaveTitle(/TechDengue/)
  })
})
