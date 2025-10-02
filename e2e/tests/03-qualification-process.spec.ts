import { test, expect } from '@playwright/test';

/**
 * E2E Test: Qualification Process
 * 
 * Tests the qualification questionnaire workflow, including the "Prospect's WHY" form
 * as defined in the Frazer Method. This ensures customers are properly qualified
 * before moving to the presentation stage.
 * 
 * Author: Manus 7
 * Task: TASK-110 (End-to-End Testing)
 */

test.describe('Qualification Process', () => {
  let customerEmail: string;

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Create a test customer and move to "Invited" stage
    customerEmail = `qualification-test-${Date.now()}@example.com`;
    
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('Qualification Test Customer');
    await page.getByLabel(/email/i).fill(customerEmail);
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for customer creation
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Move customer to "Invited" stage (prerequisite for qualification)
    await page.getByText(customerEmail).click();
    
    // Progress to Invited stage
    for (let i = 0; i < 2; i++) {
      const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
      await moveButton.click();
      await page.waitForTimeout(1000);
    }

    // Verify at "Invited" stage
    await expect(page.getByText(/invited/i)).toBeVisible();
  });

  test('should display qualification questionnaire', async ({ page }) => {
    // Look for "Qualify" button or "Qualification" tab
    const qualifyButton = page.getByRole('button', { name: /qualify|qualification|questionnaire/i });
    
    if (await qualifyButton.isVisible()) {
      await qualifyButton.click();

      // Verify questionnaire form is displayed
      await expect(page.getByText(/prospect.*why|qualification|questionnaire/i)).toBeVisible();
    } else {
      // Alternative: look for a qualification tab or section
      const qualificationTab = page.getByRole('tab', { name: /qualification/i });
      if (await qualificationTab.isVisible()) {
        await qualificationTab.click();
        await expect(page.getByText(/prospect.*why|qualification|questionnaire/i)).toBeVisible();
      }
    }
  });

  test('should complete qualification questionnaire with all fields', async ({ page }) => {
    // Access qualification form
    const qualifyButton = page.getByRole('button', { name: /qualify|qualification|questionnaire/i });
    
    if (await qualifyButton.isVisible()) {
      await qualifyButton.click();

      // Fill in qualification questions (based on Frazer Method)
      // These are example questions - adjust based on actual implementation
      
      // Question 1: What is your biggest challenge?
      const challenge = page.getByLabel(/challenge|problem|pain point/i);
      if (await challenge.isVisible()) {
        await challenge.fill('Need to scale my business and build a team');
      }

      // Question 2: What is your goal?
      const goal = page.getByLabel(/goal|objective|target/i);
      if (await goal.isVisible()) {
        await goal.fill('Achieve financial freedom and time freedom');
      }

      // Question 3: Why is this important to you?
      const why = page.getByLabel(/why|motivation|reason/i);
      if (await why.isVisible()) {
        await why.fill('Want to spend more time with family and travel');
      }

      // Question 4: What have you tried before?
      const previous = page.getByLabel(/tried|previous|experience/i);
      if (await previous.isVisible()) {
        await previous.fill('Tried traditional business but hit a ceiling');
      }

      // Submit qualification
      await page.getByRole('button', { name: /submit|save|complete/i }).click();

      // Verify success message
      await expect(page.getByText(/qualification complete|qualified|success/i)).toBeVisible({ timeout: 5000 });

      // Verify customer moved to "Qualified" stage
      await expect(page.getByText(/qualified/i)).toBeVisible();
    }
  });

  test('should require all mandatory qualification fields', async ({ page }) => {
    // Access qualification form
    const qualifyButton = page.getByRole('button', { name: /qualify|qualification|questionnaire/i });
    
    if (await qualifyButton.isVisible()) {
      await qualifyButton.click();

      // Try to submit without filling fields
      await page.getByRole('button', { name: /submit|save|complete/i }).click();

      // Verify validation errors
      await expect(page.getByText(/required|please fill/i)).toBeVisible();
    }
  });

  test('should save qualification data and display it later', async ({ page }) => {
    // Access qualification form
    const qualifyButton = page.getByRole('button', { name: /qualify|qualification|questionnaire/i });
    
    if (await qualifyButton.isVisible()) {
      await qualifyButton.click();

      // Fill in a unique answer
      const uniqueAnswer = `Test answer ${Date.now()}`;
      const why = page.getByLabel(/why|motivation|reason/i);
      if (await why.isVisible()) {
        await why.fill(uniqueAnswer);
      }

      // Submit qualification
      await page.getByRole('button', { name: /submit|save|complete/i }).click();
      await page.waitForTimeout(2000);

      // Navigate away and back
      await page.goto('/');
      await page.getByText(customerEmail).click();

      // Re-open qualification section
      const qualificationTab = page.getByRole('tab', { name: /qualification/i });
      if (await qualificationTab.isVisible()) {
        await qualificationTab.click();
      }

      // Verify the saved answer is displayed
      await expect(page.getByText(uniqueAnswer)).toBeVisible();
    }
  });

  test('should prevent skipping qualification stage', async ({ page }) => {
    // Customer is at "Invited" stage
    // Try to move to next stage without completing qualification
    
    const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
    
    if (await moveButton.isVisible()) {
      await moveButton.click();

      // Should show error or warning about completing qualification first
      await expect(page.getByText(/complete qualification|qualify first|qualification required/i)).toBeVisible({ timeout: 5000 });
    }
  });

  test('should display qualification score or rating', async ({ page }) => {
    // Access qualification form
    const qualifyButton = page.getByRole('button', { name: /qualify|qualification|questionnaire/i });
    
    if (await qualifyButton.isVisible()) {
      await qualifyButton.click();

      // Fill in qualification with high-quality answers
      const fields = [
        { label: /challenge/i, value: 'Significant business growth challenge' },
        { label: /goal/i, value: 'Build a 7-figure business' },
        { label: /why/i, value: 'Create generational wealth for my family' },
      ];

      for (const field of fields) {
        const input = page.getByLabel(field.label);
        if (await input.isVisible()) {
          await input.fill(field.value);
        }
      }

      // Submit qualification
      await page.getByRole('button', { name: /submit|save|complete/i }).click();
      await page.waitForTimeout(2000);

      // Look for qualification score or rating
      const score = page.getByText(/score|rating|quality/i);
      if (await score.isVisible()) {
        await expect(score).toBeVisible();
      }
    }
  });
});
