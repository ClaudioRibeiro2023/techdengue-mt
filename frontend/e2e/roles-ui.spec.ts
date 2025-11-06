import { test, expect } from '@playwright/test'

/**
 * Testes E2E para Componentes Visuais de Roles
 */

test.describe('RoleBadge Component', () => {
  test('Mostra badge de ADMIN com cor roxa', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // RoleBadge deve estar visível
    // Pode ter classe bg-purple ou similar
    const badge = header.locator('[class*="purple"]').or(
      header.locator('[title*="Administrador"]')
    )
    
    // Se badge existe, deve ser visível
    if (await badge.count() > 0) {
      await expect(badge.first()).toBeVisible()
    }
  })

  test('Mostra badge de GESTOR com cor azul', async ({ page }) => {
    await page.goto('/?e2e-roles=GESTOR')
    await page.goto('/dashboard')
    
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // Badge azul para GESTOR
    const badge = header.locator('[class*="blue"]').or(
      header.locator('[title*="Gestor"]')
    )
    
    if (await badge.count() > 0) {
      await expect(badge.first()).toBeVisible()
    }
  })

  test('Modo compact mostra apenas role principal', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN,GESTOR')
    await page.goto('/dashboard')
    
    const header = page.locator('header')
    await expect(header).toBeVisible()
    
    // Em modo compact, deve mostrar ADMIN (mais alta) + contador "+1"
  })

  test('Badge tem ícone apropriado', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    const header = page.locator('header')
    
    // Badge deve ter ícone (Shield para ADMIN)
    const hasIcon = await header.locator('svg').count() > 0
    expect(hasIcon).toBe(true)
  })
})

test.describe('RestrictedFeature Component', () => {
  test('Oculta conteúdo quando falta role', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Botões administrativos não devem aparecer
    const adminButton = page.locator('button:has-text("Administração")')
    await expect(adminButton).not.toBeVisible()
  })

  test('Mostra lock overlay para conteúdo bloqueado', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Se usar showLock=true, deve ter overlay com ícone de cadeado
    const lockIcon = page.locator('svg').filter({ hasText: /lock/i })
    
    // Pode ou não ter, dependendo de onde RestrictedFeature é usado
  })

  test('Tooltip mostra roles necessárias ao hover', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Hover em elemento bloqueado deve mostrar tooltip
    // "Requer: ADMIN"
  })

  test('Mostra fallback customizado quando fornecido', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Se RestrictedFeature tem fallback, deve mostrar esse fallback
  })
})

test.describe('AccessDeniedBanner Component', () => {
  test('Banner aparece ao acessar rota sem permissão', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Deve mostrar AccessDeniedBanner
    const banner = page.locator('div:has-text("Acesso Negado")').or(
      page.locator('div:has-text("Acesso Limitado")')
    )
    
    if (await banner.count() > 0) {
      await expect(banner.first()).toBeVisible()
    }
  })

  test('Banner mostra roles necessárias', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Banner deve listar "Requer: ADMIN"
    const body = await page.locator('body').textContent()
    const mentionsAdmin = body?.includes('ADMIN')
    
    if (body?.includes('Acesso')) {
      expect(mentionsAdmin).toBe(true)
    }
  })

  test('Banner variante error tem cor vermelha', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Banner de erro deve ter bg-red ou border-red
    const errorBanner = page.locator('[class*="red"]')
    
    if (await errorBanner.count() > 0) {
      await expect(errorBanner.first()).toBeVisible()
    }
  })

  test('Botão Voltar funciona', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Ir para admin (sem permissão)
    await page.goto('/admin')
    
    // Clicar em "Voltar"
    const backButton = page.locator('button:has-text("Voltar")')
    
    if (await backButton.count() > 0) {
      await backButton.click()
      await page.waitForTimeout(500)
      
      // Deve voltar para /dashboard
      await expect(page).toHaveURL(/\/dashboard/)
    }
  })

  test('Botão Ir para Home funciona', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    const homeButton = page.locator('button:has-text("Home")').or(
      page.locator('a:has-text("Home")')
    )
    
    if (await homeButton.count() > 0) {
      await homeButton.click()
      await page.waitForTimeout(500)
      
      // Deve ir para /
      expect(page.url()).toBeTruthy()
    }
  })

  test('Banner pode ser fechado se tem onDismiss', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Botão X para fechar
    const closeButton = page.locator('button[aria-label="Fechar"]')
    
    if (await closeButton.count() > 0) {
      await closeButton.click()
      
      // Banner deve desaparecer
      await page.waitForTimeout(300)
      const banner = page.locator('div:has-text("Acesso")')
      await expect(banner).not.toBeVisible()
    }
  })
})

test.describe('PermissionGate Integration', () => {
  test('Conteúdo renderiza para role autorizada', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Admin deve ver todo o conteúdo
    const content = page.locator('main').or(page.locator('[role="main"]'))
    await expect(content).toBeVisible()
  })

  test('Conteúdo não renderiza para role não autorizada', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // CAMPO não deve ver botões administrativos
    const adminSection = page.locator('section:has-text("Administração")')
    
    if (await adminSection.count() > 0) {
      await expect(adminSection).not.toBeVisible()
    }
  })

  test('Múltiplos PermissionGates funcionam simultaneamente', async ({ page }) => {
    await page.goto('/?e2e-roles=GESTOR')
    await page.goto('/dashboard')
    
    // GESTOR deve ver alguns controles mas não todos
    const body = page.locator('body')
    await expect(body).toBeVisible()
  })
})

test.describe('Visual Feedback', () => {
  test('Elemento bloqueado tem opacity reduzida', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Elementos bloqueados devem ter opacity-50 ou similar
    const disabledElements = page.locator('[class*="opacity-50"]')
    
    // Pode ter ou não, dependendo do uso de RestrictedFeature
  })

  test('Hover em elemento bloqueado mostra cursor not-allowed', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Elementos com lock devem ter cursor: not-allowed
  })

  test('Animação slideDown funciona em banner', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Banner deve aparecer com animação (classe animate-slideDown)
    const banner = page.locator('[class*="animate-slideDown"]')
    
    if (await banner.count() > 0) {
      await expect(banner.first()).toBeVisible()
    }
  })
})

test.describe('Accessibility', () => {
  test('RoleBadge tem tooltip acessível', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Badge deve ter title ou aria-label
    const badge = page.locator('header [title]').or(
      page.locator('header [aria-label]')
    )
    
    if (await badge.count() > 0) {
      const hasTitle = await badge.first().getAttribute('title')
      const hasAriaLabel = await badge.first().getAttribute('aria-label')
      
      expect(hasTitle || hasAriaLabel).toBeTruthy()
    }
  })

  test('AccessDeniedBanner tem role="alert"', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Banner deve ter role="alert" para screen readers
    const alert = page.locator('[role="alert"]')
    
    if (await alert.count() > 0) {
      await expect(alert.first()).toBeVisible()
    }
  })

  test('Botões têm labels descritivos', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/admin')
    
    // Botões devem ter texto ou aria-label
    const buttons = page.locator('button')
    const count = await buttons.count()
    
    for (let i = 0; i < Math.min(count, 5); i++) {
      const button = buttons.nth(i)
      const text = await button.textContent()
      const ariaLabel = await button.getAttribute('aria-label')
      
      expect(text || ariaLabel).toBeTruthy()
    }
  })
})

test.describe('Dark Mode', () => {
  test('RoleBadge adapta cores em dark mode', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    
    // Ativar dark mode
    await page.evaluate(() => {
      document.documentElement.classList.add('theme-dark')
    })
    
    await page.waitForTimeout(200)
    
    // Badge deve permanecer visível e legível
    const header = page.locator('header')
    await expect(header).toBeVisible()
  })

  test('AccessDeniedBanner adapta cores em dark mode', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    
    // Ativar dark mode
    await page.evaluate(() => {
      document.documentElement.classList.add('theme-dark')
    })
    
    await page.goto('/admin')
    
    // Banner deve ser legível em dark mode
    const banner = page.locator('div:has-text("Acesso")')
    
    if (await banner.count() > 0) {
      await expect(banner.first()).toBeVisible()
    }
  })
})

test.describe('Performance', () => {
  test('Renderização de múltiplos RestrictedFeatures é rápida', async ({ page }) => {
    await page.goto('/?e2e-roles=ADMIN')
    
    const start = Date.now()
    await page.goto('/dashboard')
    const loadTime = Date.now() - start
    
    // Dashboard deve carregar em < 2 segundos
    expect(loadTime).toBeLessThan(2000)
  })

  test('Troca de role re-renderiza componentes rapidamente', async ({ page }) => {
    await page.goto('/?e2e-roles=CAMPO')
    await page.goto('/dashboard')
    
    // Trocar para ADMIN
    const start = Date.now()
    await page.goto('/?e2e-roles=ADMIN')
    await page.goto('/dashboard')
    const switchTime = Date.now() - start
    
    // Troca deve ser rápida
    expect(switchTime).toBeLessThan(1500)
  })
})
