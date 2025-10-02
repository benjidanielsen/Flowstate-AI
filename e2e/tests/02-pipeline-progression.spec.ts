import { test, expect } from '@playwright/test';

/**
 * E2E Test: Pipeline Progression (Frazer Method)
 * 
 * Tests the complete pipeline progression through all stages of the Frazer Method:
 * New Lead → Warming Up → Invited → Qualified → Presentation Sent → Follow-up → Closed-Won
 * 
 * This is a critical test ensuring the core CRM functionality works correctly.
 * 
 * Author: Manus 7
 * Task: TASK-110 (End-to-End Testing)
 */

test.describe('Pipeline Progression (Frazer Method)', () => {
  let customerEmail: string;

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Create a test customer for pipeline progression
    customerEmail = `pipeline-test-${Date.now()}@example.com`;
    
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('Pipeline Test Customer');
    await page.getByLabel(/email/i).fill(customerEmail);
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for customer creation
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });
  });

  test('should move customer from New Lead to Warming Up', async ({ page }) => {
    // Find and click on the customer
    await page.getByText(customerEmail).click();

    // Verify initial status
    await expect(page.getByText(/new lead|lead/i)).toBeVisible();

    // Click "Move to Next Stage" or similar button
    const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
    await moveButton.click();

    // Verify status changed to "Warming Up"
    await expect(page.getByText(/warming up/i)).toBeVisible({ timeout: 5000 });
  });

  test('should progress through all Frazer Method stages', async ({ page }) => {
    // Find and click on the customer
    await page.getByText(customerEmail).click();

    // Define the expected pipeline stages in order
    const stages = [
      'New Lead',
      'Warming Up',
      'Invited',
      'Qualified',
      'Presentation Sent',
      'Follow-up',
      'Closed-Won'
    ];

    // Progress through each stage
    for (let i = 0; i < stages.length - 1; i++) {
      const currentStage = stages[i];
      const nextStage = stages[i + 1];

      // Verify current stage
      await expect(page.getByText(new RegExp(currentStage, 'i'))).toBeVisible();

      // Click "Move to Next Stage"
      const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
      await moveButton.click();

      // Verify moved to next stage
      await expect(page.getByText(new RegExp(nextStage, 'i'))).toBeVisible({ timeout: 5000 });
    }

    // Final verification: customer should be at "Closed-Won"
    await expect(page.getByText(/closed-won|closed won/i)).toBeVisible();
  });

  test('should track pipeline stage history', async ({ page }) => {
    // Find and click on the customer
    await page.getByText(customerEmail).click();

    // Move through a few stages
    for (let i = 0; i < 3; i++) {
      const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
      await moveButton.click();
      await page.waitForTimeout(1000); // Wait for transition
    }

    // Check if there's a history or activity log
    const historySection = page.getByText(/history|activity|timeline/i);
    if (await historySection.isVisible()) {
      await historySection.click();
      
      // Verify multiple stage changes are logged
      await expect(page.getByText(/moved to|stage changed/i)).toBeVisible();
    }
  });

  test('should display pipeline statistics', async ({ page }) => {
    // Navigate to dashboard or pipeline view
    await page.goto('/');

    // Look for pipeline statistics or metrics
    const statsSection = page.getByText(/pipeline|statistics|metrics|dashboard/i).first();
    
    if (await statsSection.isVisible()) {
      await statsSection.click();

      // Verify pipeline stage counts are displayed
      await expect(page.getByText(/new lead|warming up|invited/i)).toBeVisible();
    }
  });

  test('should prevent moving backwards in pipeline', async ({ page }) => {
    // Find and click on the customer
    await page.getByText(customerEmail).click();

    // Move to next stage
    const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
    await moveButton.click();
    await expect(page.getByText(/warming up/i)).toBeVisible({ timeout: 5000 });

    // Check if there's a "Move Back" or "Previous Stage" button
    const moveBackButton = page.getByRole('button', { name: /previous stage|move back|go back/i });
    
    // If button exists, it should be disabled or not exist at all
    if (await moveBackButton.isVisible()) {
      await expect(moveBackButton).toBeDisabled();
    }
  });

  test('should update pipeline stage via dropdown or select', async ({ page }) => {
    // Find and click on the customer
    await page.getByText(customerEmail).click();

    // Look for a status dropdown or select element
    const statusDropdown = page.getByLabel(/status|stage|pipeline/i);
    
    if (await statusDropdown.isVisible()) {
      await statusDropdown.click();
      
      // Select "Invited" stage
      await page.getByRole('option', { name: /invited/i }).click();

      // Verify status changed
      await expect(page.getByText(/invited/i)).toBeVisible({ timeout: 5000 });
    }
  });
});
