import { test, expect, Page } from '@playwright/test'

async function gotoModule(page: Page, path = '/modulos/previsao-simulacao') {
  await page.goto(path)
  await expect(page.locator('#app-submenu .module-name')).toHaveText('Previsão & Simulação')
}

async function clearPersisted(page: Page) {
  await page.goto('/')
  await page.evaluate(() => {
    try {
      localStorage.removeItem('sidebar-collapsed')
      localStorage.removeItem('subnav-collapsed')
      localStorage.removeItem('functions-collapsed')
    } catch { /* no-op */ }
  })
}

test.describe('Collapse persistence', () => {
  test('AppSidebar collapse persists across reload', async ({ page }) => {
    await clearPersisted(page)
    await gotoModule(page)

    const btn = page.locator('#app-sidebar .collapse-btn')
    await expect(btn).toBeVisible()
    await btn.click()

    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('sidebar-collapsed'))).toBeTruthy()
    await expect.poll(async () => page.evaluate(() => localStorage.getItem('sidebar-collapsed'))).toBe('1')

    await page.reload()

    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('sidebar-collapsed'))).toBeTruthy()
  })

  test('Submenu collapse persists across reload', async ({ page }) => {
    await clearPersisted(page)
    await gotoModule(page)

    const btn = page.locator('#app-submenu .collapse-btn')
    await expect(btn).toBeVisible()
    await btn.click()

    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('subnav-collapsed'))).toBeTruthy()
    await expect.poll(async () => page.evaluate(() => localStorage.getItem('subnav-collapsed'))).toBe('1')

    await page.reload()

    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('subnav-collapsed'))).toBeTruthy()
  })
})
