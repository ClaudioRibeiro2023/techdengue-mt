import { test, expect } from '@playwright/test';

/**
 * E2E Tests - Authentication Flow
 */

test.describe('Autenticação', () => {
  test('deve exibir página de login ao acessar sem autenticação', async ({ page }) => {
    await page.goto('/');
    
    // Deve redirecionar para Keycloak ou mostrar botão de login
    await expect(page).toHaveURL(/login|auth|keycloak/i);
  });

  test('deve fazer login com credenciais válidas', async ({ page, context }) => {
    await page.goto('/');
    
    // Assumindo redirecionamento para Keycloak
    await page.waitForURL(/keycloak/i, { timeout: 10000 });
    
    // Preencher credenciais
    await page.fill('input[name="username"]', 'test@techdengue.mt.gov.br');
    await page.fill('input[name="password"]', 'Test@123');
    
    // Submeter
    await page.click('button[type="submit"]');
    
    // Aguardar callback e redirecionamento
    await page.waitForURL(/callback/, { timeout: 30000 });
    await page.waitForURL('/', { timeout: 30000 });
    
    // Verificar que está autenticado
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('deve rejeitar login com credenciais inválidas', async ({ page }) => {
    await page.goto('/');
    await page.waitForURL(/keycloak/i);
    
    await page.fill('input[name="username"]', 'invalid@test.com');
    await page.fill('input[name="password"]', 'wrongpass');
    await page.click('button[type="submit"]');
    
    // Deve mostrar erro
    await expect(page.locator('.alert-error, .error-message')).toBeVisible();
  });

  test('deve fazer logout corretamente', async ({ page }) => {
    // Assumindo já autenticado (usar storage state)
    await page.goto('/');
    
    // Click no menu do usuário
    await page.click('[data-testid="user-menu"]');
    
    // Click em logout
    await page.click('[data-testid="logout-button"]');
    
    // Deve redirecionar para login
    await expect(page).toHaveURL(/login|auth|keycloak/i);
  });

  test('deve renovar token automaticamente', async ({ page }) => {
    await page.goto('/');
    
    // Aguardar 5 minutos para testar silent renew
    // (em prod o token expira em 5min, silent renew ocorre automaticamente)
    await page.waitForTimeout(5 * 60 * 1000);
    
    // Fazer requisição que exige token
    await page.click('[data-testid="dashboard-link"]');
    
    // Não deve redirecionar para login
    await expect(page).not.toHaveURL(/login/i);
  });
});
