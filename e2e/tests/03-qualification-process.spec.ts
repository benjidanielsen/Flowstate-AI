import { test, expect } from '@playwright/test';
import { prepareAuthenticatedPage, createCustomerViaApi } from '../utils/auth';

test.describe('Customer detail management', () => {
  test.beforeEach(async ({ page }) => {
    await prepareAuthenticatedPage(page, '/customers');
  });

  test('allows editing customer contact information', async ({ page }) => {
    const customer = await createCustomerViaApi();

    await page.reload();
    await page.waitForResponse((response) =>
      response.url().includes('/api/customers') && response.request().method() === 'GET'
    );

    await page.getByRole('link', { name: customer.name }).click();
    await page.waitForResponse((response) =>
      response.url().includes(`/api/customers/${customer.id}`) && response.request().method() === 'GET'
    );
    await expect(page.getByRole('heading', { name: customer.name })).toBeVisible();

    await page.getByRole('button', { name: /edit/i }).click();
    const updatedPhone = '+1-555-4242';
    await page.fill('#edit-phone', updatedPhone);
    await page.getByRole('button', { name: /save changes/i }).click();

    await expect(page.getByRole('button', { name: /^edit$/i })).toBeVisible({ timeout: 5000 });
    await expect(page.locator('a').filter({ hasText: updatedPhone })).toBeVisible({ timeout: 5000 });
  });
});
