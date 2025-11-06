import { test, expect, Page } from '@playwright/test'

async function setRoles(page: Page, roles: string) {
  await page.goto('/')
  await page.evaluate((r: string) => {
    localStorage.clear()
    localStorage.setItem('e2e-roles', r)
  }, roles)
  await page.reload()
}

function linkInSidebar(page: Page, name: string) {
  const sidebar = page.locator('#app-sidebar')
  return sidebar.locator('nav.app-nav a', { hasText: name })
}

// Only assert modules with role restrictions to avoid false positives
// Visible when ADMIN only: Observabilidade, ETL & Integração, Administração, Previsão & Simulação
// Hidden when ADMIN only: Vigilância Entomológica, Vigilância Epidemiológica, Resposta Operacional

test.describe('Role-based navigation visibility', () => {
  test('ADMIN role shows admin-only modules and hides vigilancia/campo', async ({ page }) => {
    await setRoles(page, 'ADMIN')

    await expect(linkInSidebar(page, 'Observabilidade')).toBeVisible()
    await expect(linkInSidebar(page, 'ETL & Integração')).toBeVisible()
    await expect(linkInSidebar(page, 'Administração')).toBeVisible()
    await expect(linkInSidebar(page, 'Previsão & Simulação')).toBeVisible()

    await expect(linkInSidebar(page, 'Vigilância Entomológica')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Vigilância Epidemiológica')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Resposta Operacional')).toHaveCount(0)
  })

  test('GESTOR role shows gestão/vigilância/campo and hides admin-only', async ({ page }) => {
    await setRoles(page, 'GESTOR')

    await expect(linkInSidebar(page, 'Previsão & Simulação')).toBeVisible()
    await expect(linkInSidebar(page, 'Vigilância Entomológica')).toBeVisible()
    await expect(linkInSidebar(page, 'Vigilância Epidemiológica')).toBeVisible()
    await expect(linkInSidebar(page, 'Resposta Operacional')).toBeVisible()
    await expect(linkInSidebar(page, 'Administração')).toBeVisible()

    await expect(linkInSidebar(page, 'Observabilidade')).toHaveCount(0)
    await expect(linkInSidebar(page, 'ETL & Integração')).toHaveCount(0)
  })

  test('VIGILANCIA role shows vigilancia and hides admin/etl/observability/campo', async ({ page }) => {
    await setRoles(page, 'VIGILANCIA')

    await expect(linkInSidebar(page, 'Previsão & Simulação')).toBeVisible()
    await expect(linkInSidebar(page, 'Vigilância Entomológica')).toBeVisible()
    await expect(linkInSidebar(page, 'Vigilância Epidemiológica')).toBeVisible()

    await expect(linkInSidebar(page, 'Administração')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Observabilidade')).toHaveCount(0)
    await expect(linkInSidebar(page, 'ETL & Integração')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Resposta Operacional')).toHaveCount(0)
  })

  test('CAMPO role shows only operacional and hides admin/dados/vigilância', async ({ page }) => {
    await setRoles(page, 'CAMPO')

    await expect(linkInSidebar(page, 'Resposta Operacional')).toBeVisible()

    await expect(linkInSidebar(page, 'Previsão & Simulação')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Administração')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Observabilidade')).toHaveCount(0)
    await expect(linkInSidebar(page, 'ETL & Integração')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Vigilância Entomológica')).toHaveCount(0)
    await expect(linkInSidebar(page, 'Vigilância Epidemiológica')).toHaveCount(0)
  })
})
