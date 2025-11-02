import { test, expect } from '@playwright/test';

/**
 * E2E Tests - Dashboard EPI
 */

test.describe('Dashboard EPI', () => {
  test.beforeEach(async ({ page }) => {
    // Assumindo autenticado via storage state
    await page.goto('/dashboard');
  });

  test('deve carregar KPIs corretamente', async ({ page }) => {
    // Aguardar carregamento
    await page.waitForSelector('[data-testid="kpi-card"]', { timeout: 10000 });
    
    // Verificar se pelo menos 4 KPIs foram carregados
    const kpiCards = page.locator('[data-testid="kpi-card"]');
    await expect(kpiCards).toHaveCount(4, { timeout: 10000 });
    
    // Verificar conteúdo dos KPIs
    await expect(page.locator('text=Total de Casos')).toBeVisible();
    await expect(page.locator('text=Óbitos')).toBeVisible();
    await expect(page.locator('text=Letalidade')).toBeVisible();
    await expect(page.locator('text=Incidência')).toBeVisible();
  });

  test('deve aplicar filtros e recarregar dados', async ({ page }) => {
    // Selecionar ano
    await page.selectOption('[data-testid="filter-ano"]', '2023');
    
    // Aguardar recarregamento (spinner ou loading state)
    await page.waitForLoadState('networkidle');
    
    // Verificar que dados mudaram
    const kpiValue = await page.locator('[data-testid="kpi-total-casos"]').textContent();
    expect(kpiValue).toBeTruthy();
  });

  test('deve exibir gráfico de série temporal', async ({ page }) => {
    // Aguardar gráfico carregar
    await page.waitForSelector('canvas', { timeout: 10000 });
    
    // Verificar que canvas está visível
    const canvas = page.locator('canvas').first();
    await expect(canvas).toBeVisible();
    
    // Verificar dimensões do canvas
    const box = await canvas.boundingBox();
    expect(box).not.toBeNull();
    expect(box!.width).toBeGreaterThan(0);
    expect(box!.height).toBeGreaterThan(0);
  });

  test('deve exibir ranking top 10 municípios', async ({ page }) => {
    // Aguardar tabela/gráfico de ranking
    await page.waitForSelector('[data-testid="top-n-chart"]', { timeout: 10000 });
    
    // Verificar se pelo menos 5 municípios aparecem
    const items = page.locator('[data-testid="ranking-item"]');
    const count = await items.count();
    expect(count).toBeGreaterThanOrEqual(5);
  });

  test('deve alternar entre diferentes doenças', async ({ page }) => {
    // Selecionar dengue
    await page.selectOption('[data-testid="filter-doenca"]', 'DENGUE');
    await page.waitForLoadState('networkidle');
    
    const kpiDengue = await page.locator('[data-testid="kpi-total-casos"]').textContent();
    
    // Selecionar zika
    await page.selectOption('[data-testid="filter-doenca"]', 'ZIKA');
    await page.waitForLoadState('networkidle');
    
    const kpiZika = await page.locator('[data-testid="kpi-total-casos"]').textContent();
    
    // Valores devem ser diferentes
    expect(kpiDengue).not.toBe(kpiZika);
  });

  test('deve exibir variação percentual nos KPIs', async ({ page }) => {
    // Verificar se setas de tendência aparecem
    const trendingIcons = page.locator('[data-testid="kpi-trend"]');
    const count = await trendingIcons.count();
    expect(count).toBeGreaterThan(0);
  });

  test('deve ser responsivo em mobile', async ({ page }) => {
    // Redimensionar para mobile
    await page.setViewportSize({ width: 375, height: 667 });
    
    // KPIs devem empilhar verticalmente
    const kpiCards = page.locator('[data-testid="kpi-card"]');
    const firstCard = kpiCards.first();
    const secondCard = kpiCards.nth(1);
    
    const firstBox = await firstCard.boundingBox();
    const secondBox = await secondCard.boundingBox();
    
    // Segunda carta deve estar abaixo da primeira (não ao lado)
    expect(secondBox!.y).toBeGreaterThan(firstBox!.y + firstBox!.height);
  });

  test('performance: deve carregar em menos de 4 segundos', async ({ page }) => {
    const startTime = Date.now();
    
    await page.goto('/dashboard');
    await page.waitForSelector('[data-testid="kpi-card"]', { timeout: 10000 });
    
    const loadTime = Date.now() - startTime;
    
    // SLO: p95 ≤ 4s
    expect(loadTime).toBeLessThan(4000);
    console.log(`Dashboard load time: ${loadTime}ms`);
  });
});
