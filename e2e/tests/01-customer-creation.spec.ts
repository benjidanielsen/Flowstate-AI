import { test, expect } from '@playwright/test';
import { prepareAuthenticatedPage } from '../utils/auth';

test.describe('Customer management', () => {
  test.beforeEach(async ({ page }) => {
    await prepareAuthenticatedPage(page, '/customers');
  });

  test('allows creating a new customer from the list view', async ({ page }) => {
    const uniqueSuffix = Date.now();
    const customerName = `Test Customer ${uniqueSuffix}`;
    const email = `customer-${uniqueSuffix}@example.com`;

    await page.getByRole('button', { name: /add customer/i }).click();
    await page.fill('#customer-name', customerName);
    await page.fill('#customer-email', email);
    await page.fill('#customer-phone', '+1-555-0000');

    const [response] = await Promise.all([
      page.waitForResponse((res) => res.url().includes('/api/customers') && res.request().method() === 'POST'),
      page.getByRole('button', { name: /create customer/i }).click()
    ]);

    if (!response.ok()) {
      const body = await response.text();
      throw new Error(`Customer creation failed (${response.status()}): ${body}`);
    }

    const created = await response.json();
    expect(created.name).toBe(customerName);
    expect(created.email).toBe(email);

    await expect(page.getByRole('button', { name: /add customer/i })).toBeVisible();
  });

  test('disables creation until required fields are populated', async ({ page }) => {
    await page.getByRole('button', { name: /add customer/i }).click();

    const createButton = page.getByRole('button', { name: /create customer/i });
    await expect(createButton).toBeDisabled();

    await page.fill('#customer-name', 'Temporary Name');
    await expect(createButton).toBeEnabled();

    await page.fill('#customer-name', '');
    await expect(createButton).toBeDisabled();

    await page.getByRole('button', { name: /cancel/i }).click();
    await expect(createButton).not.toBeVisible();
  });
});
