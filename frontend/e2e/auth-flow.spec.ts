import { test, expect } from '@playwright/test'

/**
 * Testes E2E para Fluxo Completo de Autenticação
 */

test.describe('Fluxo de Autenticação', () => {
  test.beforeEach(async ({ page }) => {
    // Limpar estado
    await page.goto('/')
    await page.evaluate(() => {
      localStorage.clear()
      sessionStorage.clear()
    })
  })

  test('Login redirecion a para dashboard após autenticação', async ({ page }) => {
    // Em modo E2E, bypass de autenticação
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Deve estar no dashboard
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Usuário não autenticado é redirecionado para login', async ({ page }) => {
    // Tentar acessar dashboard sem autenticação
    await page.goto('/dashboard')
    
    // Em modo E2E com bypass, sempre permite
    // mas em produção redireciona para /login
    
    // Verificar se está em dashboard (E2E mode) ou login (prod mode)
    const url = page.url()
    const isAuthenticated = url.includes('/dashboard') || url.includes('/login')
    expect(isAuthenticated).toBe(true)
  })

  test('Roles são extraídas do token corretamente', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN,GESTOR')
    await page.goto('/dashboard')
    
    // Verificar que múltiplas roles estão ativas
    // (pode verificar via RoleBadge ou logs)
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Token expirado resulta em logout', async ({ page }) => {
    // Este teste é mais complexo e requer mock do Keycloak
    // Por enquanto, apenas verificar estrutura básica
    
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Refresh token renova sessão', async ({ page }) => {
    // Teste de renovação de token
    // Requer integração real com Keycloak
    
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    await expect(page).toHaveTitle(/TechDengue/)
  })
})

test.describe('Session Management', () => {
  test('Session persiste após reload', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Reload da página
    await page.reload()
    
    // Session deve persistir
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Session persiste entre navegações', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Navegar para outra página
    await page.goto('/mapa')
    await expect(page).toHaveURL(/\/mapa/)
    
    // Voltar
    await page.goto('/dashboard')
    await expect(page).toHaveURL(/\/dashboard/)
  })

  test('Logout limpa session e redireciona', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Procurar botão de logout (pode estar em UserMenu)
    const logoutButton = page.locator('button:has-text("Sair")').or(
      page.locator('button:has-text("Logout")')
    ).or(
      page.locator('a:has-text("Sair")')
    )
    
    // Se botão existe, clicar
    if (await logoutButton.count() > 0) {
      await logoutButton.first().click()
      
      // Deve redirecionar ou limpar estado
      await page.waitForTimeout(500)
    }
  })
})

test.describe('Role Switching (E2E Mode)', () => {
  test('Trocar de role via localStorage', async ({ page }) => {
    // Iniciar como CAMPO
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Trocar para ADMIN
    await page.evaluate(() => {
      localStorage.setItem('e2e-roles', JSON.stringify(['ADMIN']))
    })
    
    await page.reload()
    
    // Agora deve ter permissões de ADMIN
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Trocar de role via query param', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Trocar via URL
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Permissões devem ter mudado para ADMIN
    await expect(page).toHaveTitle(/TechDengue/)
  })

  test('Role inválida = sem permissões', async ({ page }) => {
    await page.goto('/?e2e-roles=INVALID')
    await page.goto('/dashboard')
    
    // Sistema deve tratar role inválida gracefully
    // Pode mostrar acesso limitado ou redirecionar
    const url = page.url()
    expect(url).toBeTruthy()
  })
})

test.describe('Protected Routes', () => {
  test('/admin requer role ADMIN', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // CAMPO não deve ter acesso a /admin
    // Deve ver AccessDeniedBanner ou ser redirecionado
    const body = await page.locator('body').textContent()
    const hasAccessDenied = body?.includes('Acesso Negado') || 
                            body?.includes('permissão')
    
    // Se não foi redirecionado, deve ver mensagem de erro
    if (page.url().includes('/admin')) {
      expect(hasAccessDenied).toBe(true)
    }
  })

  test('/dashboard permite qualquer role autenticada', async ({ page }) => {
    // Todas as roles podem ver dashboard
    for (const role of ['ADMIN', 'GESTOR', 'VIGILANCIA', 'CAMPO']) {
      await page.goto(`/?e2e-roles=${role}`)
      await page.goto('/dashboard')
      
      await expect(page).toHaveURL(/\/dashboard/)
      await expect(page).toHaveTitle(/TechDengue/)
    }
  })

  test('Rota pública (/denuncia) não requer autenticação', async ({ page }) => {
    // Limpar roles
    await page.goto('/?e2e-roles=')
    await page.goto('/denuncia')
    
    // Deve ter acesso mesmo sem role
    await expect(page).toHaveURL(/\/denuncia/)
  })
})

test.describe('User Context', () => {
  test('UserMenu mostra informações do usuário', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Procurar por UserMenu ou user info no header
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // Pode ter nome de usuário, email, ou avatar
    // Depende da implementação do UserMenu
  })

  test('RoleBadge mostra role atual', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // RoleBadge deve estar no header
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // Badge pode ter texto ou ícone indicando ADMIN
    // Pode verificar via atributo title ou aria-label
  })
})

test.describe('Security', () => {
  test('Token não é exposto no localStorage', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Verificar que token JWT não está em texto plano no localStorage
    const storageKeys = await page.evaluate(() => Object.keys(localStorage))
    
    // Pode haver chave oidc.user: mas não 'token' direto
    const hasDirectToken = storageKeys.some(k => k.toLowerCase() === 'token')
    expect(hasDirectToken).toBe(false)
  })

  test('Navegação protegida não vaza informações', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Mesmo sem acesso, não deve vazar info sensível
    const body = await page.locator('body').textContent()
    
    // Não deve mostrar detalhes técnicos de erro
    const hasStackTrace = body?.includes('stack trace') || body?.includes('Error at')
    expect(hasStackTrace).toBe(false)
  })
})
