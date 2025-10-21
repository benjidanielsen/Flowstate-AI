import { test, expect } from '@playwright/test';
import { prepareAuthenticatedPage, createCustomerViaApi } from '../utils/auth';

test.describe('Pipeline progression', () => {
  test.beforeEach(async ({ page }) => {
    await prepareAuthenticatedPage(page, '/customers');
  });

  test('advances a customer to the next stage from the list view', async ({ page }) => {
    const customer = await createCustomerViaApi();

    await page.reload();
    await page.waitForResponse((response) =>
      response.url().includes('/api/customers') && response.request().method() === 'GET'
    );

    const customerCard = page.getByTestId(`customer-card-${customer.id}`);

    await expect(customerCard.getByText(/lead/i)).toBeVisible({ timeout: 5000 });
    await customerCard.getByTitle(/move to next stage/i).click();
    await expect(customerCard.getByText(/relationship|warming up/i)).toBeVisible({ timeout: 5000 });
  });
});
