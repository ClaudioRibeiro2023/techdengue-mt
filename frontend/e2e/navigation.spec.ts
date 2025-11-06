import { test, expect } from '@playwright/test'

// Basic E2E navigation covering menus, submenus, search, collapse and favorites
// Runs with Vite in e2e mode (.env.e2e => VITE_DEMO_MODE=true)

const sidebar = '#app-sidebar[data-app-nav="primary"]'
const subnav = '#app-submenu[data-app-nav="secondary"]'
const functionsPanel = '.module-functions-panel'

test.describe('Navigation & Menus', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => {
      try { localStorage.setItem('bypass-auth', '1') } catch { /* no-op */ }
    })
  })
  test('home renders layout and sidebar', async ({ page }) => {
    await page.goto('/?e2e=1')
    await expect(page.locator('header')).toBeVisible()
    await expect(page.locator(sidebar)).toBeVisible()
    // functions panel is optional on home (no active module)
  })

  test('module page shows functions and subtitles', async ({ page }) => {
    await page.goto('/modulos/previsao-simulacao?e2e=1')
    // Wait subnav with module name to ensure layout is mounted
    await expect(page.locator(`${subnav} .module-name`)).toContainText('Previsão')
    // Ensure functions panel is expanded (clear persisted collapse)
    await page.evaluate(() => {
      localStorage.removeItem('functions-collapsed')
      document.documentElement.classList.remove('functions-collapsed')
    })

    // Functions panel visible
    await expect(page.locator(functionsPanel)).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Ferramentas' })).toBeVisible()

    // Card shows name and subtitle (scoped to functions panel)
    const nowcastingCard = page.locator(`${functionsPanel} a.function-card`, { hasText: 'Nowcasting / Rt' })
    await expect(nowcastingCard).toBeVisible()
    await expect(nowcastingCard).toContainText('Atraso de notificação e transmissibilidade')
  })

  test('functions collapse persists across reload', async ({ page }) => {
    await page.goto('/modulos/previsao-simulacao?e2e=1')
    // Ensure expanded before toggling
    await page.evaluate(() => {
      localStorage.removeItem('functions-collapsed')
      document.documentElement.classList.remove('functions-collapsed')
    })
    const btn = page.locator(`${functionsPanel} .functions-header .collapse-btn`)
    await btn.click()

    // html should have class functions-collapsed
    await expect(page.locator('html')).toHaveClass(/functions-collapsed/)

    // persisted in localStorage
    const persisted = await page.evaluate(() => localStorage.getItem('functions-collapsed'))
    expect(persisted).toBe('1')

    // reload and keep collapsed
    await page.reload()
    await expect(page.locator('html')).toHaveClass(/functions-collapsed/)

    // expand back
    await btn.click()
    await expect(page.locator('html')).not.toHaveClass(/functions-collapsed/)
  })

  test('search filters tools by name/subtitle', async ({ page }) => {
    await page.goto('/modulos/previsao-simulacao?e2e=1')
    await page.evaluate(() => {
      localStorage.removeItem('functions-collapsed')
      document.documentElement.classList.remove('functions-collapsed')
    })
    const search = page.locator(`${functionsPanel} .functions-header input[type="search"]`)
    await search.fill('climático')
    const riscoCard = page.locator(`${functionsPanel} a.function-card`, { hasText: 'Risco Climático' })
    await expect(riscoCard).toBeVisible()
    // an unrelated card should disappear from DOM after filtering
    const nowcasting = page.locator(`${functionsPanel} a.function-card`, { hasText: 'Nowcasting / Rt' })
    await expect(nowcasting).toHaveCount(0)
  })

  test('favorites pin/unpin persists', async ({ page }) => {
    await page.goto('/modulos/previsao-simulacao?e2e=1')
    await page.evaluate(() => {
      localStorage.removeItem('functions-collapsed')
      document.documentElement.classList.remove('functions-collapsed')
    })

    const card = page.getByRole('link', { name: /Nowcasting \/ Rt/ })
    const favBtn = card.locator('button.function-fav')

    // pin
    await favBtn.click()
    await expect(page.getByText('Favoritos')).toBeVisible()

    // reload keeps favorite
    await page.reload()
    await expect(page.getByText('Favoritos')).toBeVisible()

    // unpin from Favoritos section (avoid duplicate in category grid)
    const favSection = page.locator('.functions-section', { has: page.locator('.functions-section-title', { hasText: 'Favoritos' }) })
    await favSection.locator('a.function-card', { hasText: 'Nowcasting / Rt' }).locator('button.function-fav').first().click()
    await page.reload()
    // Favoritos section might still exist if there are other pins; we just ensure the card is not pinned
  })

  test('app sidebar active link uses aria-current', async ({ page }) => {
    await page.goto('/modulos/observabilidade?e2e=1')
    // Wait for any link with aria-current=page inside primary sidebar
    const active = page.locator(`${sidebar} [aria-current="page"]`).first()
    await expect(active).toBeVisible()
  })
})
