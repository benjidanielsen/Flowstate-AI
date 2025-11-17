import { test, expect } from '@playwright/test';
import { prepareAuthenticatedPage, createCustomerViaApi } from '../utils/auth';

test.describe('Reminders', () => {
  test.beforeEach(async ({ page }) => {
    await prepareAuthenticatedPage(page, '/customers');
  });

  test('schedules a reminder for a customer', async ({ page }) => {
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

    const addReminderButton = page.getByTestId('add-reminder-button');
    await expect(addReminderButton).toBeVisible({ timeout: 5000 });
    await addReminderButton.click();
    await page.locator('#message').waitFor({ state: 'visible', timeout: 5000 });

    const reminderMessage = `Follow up with ${customer.name}`;
    const scheduledFor = new Date(Date.now() + 60 * 60 * 1000).toISOString().slice(0, 16);

    const modalForm = page.locator('form').filter({ has: page.locator('#message') });
    await modalForm.locator('#message').fill(reminderMessage);
    await modalForm.locator('#scheduledFor').fill(scheduledFor);
    await modalForm.getByRole('button', { name: /^add reminder$/i }).click();

    await expect(page.getByText(reminderMessage)).toBeVisible({ timeout: 5000 });
  });
});
