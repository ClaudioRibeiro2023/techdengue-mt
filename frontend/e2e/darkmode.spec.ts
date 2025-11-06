import { test, expect, Page } from '@playwright/test'

async function gotoAny(page: Page, path = '/modulos/previsao-simulacao') {
  await page.goto(path)
  await expect(page.locator('header')).toBeVisible()
}

test.describe('Dark mode navigation UI', () => {
  test('toggles theme-dark on root and back', async ({ page }) => {
    await gotoAny(page)

    const btn = page.getByTitle('Alternar tema')
    await expect(btn).toBeVisible()

    await btn.click()
    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('theme-dark'))).toBeTruthy()

    await btn.click()
    await expect.poll(async () => page.evaluate(() => document.documentElement.classList.contains('theme-dark'))).toBeFalsy()
  })
})
