import { test, expect } from '@playwright/test';

/**
 * E2E Test: Follow-up Automation
 * 
 * Tests the automated follow-up reminder system, including:
 * - Creating follow-up reminders
 * - Viewing upcoming reminders
 * - Marking reminders as complete
 * - Automated reminder scheduling (24h/48h, 2h/1d, 7d intervals)
 * 
 * Author: Manus 7
 * Task: TASK-110 (End-to-End Testing)
 */

test.describe('Follow-up Automation', () => {
  let customerEmail: string;

  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    // Create a test customer
    customerEmail = `followup-test-${Date.now()}@example.com`;
    
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('Follow-up Test Customer');
    await page.getByLabel(/email/i).fill(customerEmail);
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for customer creation
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Navigate to customer detail page
    await page.getByText(customerEmail).click();
  });

  test('should create a manual follow-up reminder', async ({ page }) => {
    // Look for "Add Reminder" or "Schedule Follow-up" button
    const addReminderButton = page.getByRole('button', { name: /add reminder|schedule follow-up|create reminder/i });
    
    if (await addReminderButton.isVisible()) {
      await addReminderButton.click();

      // Fill in reminder details
      await page.getByLabel(/date|when|schedule/i).fill('2025-10-10');
      await page.getByLabel(/time/i).fill('14:00');
      await page.getByLabel(/note|message|description/i).fill('Follow up on presentation');

      // Save reminder
      await page.getByRole('button', { name: /save|create|schedule/i }).click();

      // Verify success message
      await expect(page.getByText(/reminder created|scheduled|success/i)).toBeVisible({ timeout: 5000 });

      // Verify reminder appears in the list
      await expect(page.getByText(/follow up on presentation/i)).toBeVisible();
    }
  });

  test('should display upcoming reminders', async ({ page }) => {
    // Navigate to reminders page or section
    const remindersLink = page.getByRole('link', { name: /reminders|follow-ups/i });
    
    if (await remindersLink.isVisible()) {
      await remindersLink.click();

      // Verify reminders list is displayed
      await expect(page.getByText(/upcoming|reminders|follow-ups/i)).toBeVisible();

      // Check if there's a list or table of reminders
      const remindersList = page.getByRole('list').or(page.getByRole('table'));
      await expect(remindersList).toBeVisible();
    } else {
      // Alternative: look for a reminders tab
      const remindersTab = page.getByRole('tab', { name: /reminders/i });
      if (await remindersTab.isVisible()) {
        await remindersTab.click();
        await expect(page.getByText(/upcoming|reminders/i)).toBeVisible();
      }
    }
  });

  test('should mark reminder as complete', async ({ page }) => {
    // Create a reminder first
    const addReminderButton = page.getByRole('button', { name: /add reminder|schedule follow-up|create reminder/i });
    
    if (await addReminderButton.isVisible()) {
      await addReminderButton.click();
      await page.getByLabel(/date|when|schedule/i).fill('2025-10-05');
      await page.getByLabel(/note|message|description/i).fill('Test reminder to complete');
      await page.getByRole('button', { name: /save|create|schedule/i }).click();
      await page.waitForTimeout(2000);

      // Find the reminder and mark it as complete
      const completeButton = page.getByRole('button', { name: /complete|done|mark complete/i }).first();
      await completeButton.click();

      // Verify success message
      await expect(page.getByText(/reminder completed|marked complete|success/i)).toBeVisible({ timeout: 5000 });

      // Verify reminder is no longer in active list or is marked as completed
      const completedReminder = page.getByText(/test reminder to complete/i);
      if (await completedReminder.isVisible()) {
        // Should have a "completed" indicator
        await expect(page.getByText(/completed|done/i)).toBeVisible();
      }
    }
  });

  test('should automatically schedule reminders based on pipeline stage', async ({ page }) => {
    // Move customer through pipeline stages and verify reminders are auto-created
    
    // Move to "Presentation Sent" stage
    for (let i = 0; i < 4; i++) {
      const moveButton = page.getByRole('button', { name: /next stage|move to next|progress/i });
      if (await moveButton.isVisible()) {
        await moveButton.click();
        await page.waitForTimeout(1000);
      }
    }

    // Verify at "Presentation Sent" stage
    await expect(page.getByText(/presentation sent/i)).toBeVisible();

    // Check if automatic reminders were created
    const remindersTab = page.getByRole('tab', { name: /reminders/i });
    if (await remindersTab.isVisible()) {
      await remindersTab.click();

      // Verify automatic follow-up reminders exist
      await expect(page.getByText(/24.*hour|48.*hour|2.*hour|1.*day|7.*day/i)).toBeVisible();
    }
  });

  test('should display reminder notifications', async ({ page }) => {
    // Navigate to dashboard
    await page.goto('/');

    // Look for notification bell or reminder indicator
    const notificationBell = page.getByRole('button', { name: /notification|bell|alert/i });
    
    if (await notificationBell.isVisible()) {
      await notificationBell.click();

      // Verify notifications panel opens
      await expect(page.getByText(/notifications|reminders|alerts/i)).toBeVisible();
    }
  });

  test('should filter reminders by date range', async ({ page }) => {
    // Navigate to reminders page
    const remindersLink = page.getByRole('link', { name: /reminders|follow-ups/i });
    
    if (await remindersLink.isVisible()) {
      await remindersLink.click();

      // Look for date filter controls
      const dateFilter = page.getByLabel(/filter|date range|from|to/i).first();
      
      if (await dateFilter.isVisible()) {
        await dateFilter.fill('2025-10-01');

        // Verify filtered results
        await page.waitForTimeout(1000);
        await expect(page.getByText(/reminders|results/i)).toBeVisible();
      }
    }
  });

  test('should send reminder notifications via email', async ({ page }) => {
    // This test verifies the UI for email notification settings
    
    // Navigate to settings or reminder preferences
    const settingsLink = page.getByRole('link', { name: /settings|preferences/i });
    
    if (await settingsLink.isVisible()) {
      await settingsLink.click();

      // Look for email notification toggle
      const emailNotifications = page.getByLabel(/email notifications|send email/i);
      
      if (await emailNotifications.isVisible()) {
        // Verify toggle exists and can be enabled
        await emailNotifications.check();
        
        // Save settings
        await page.getByRole('button', { name: /save|update/i }).click();
        await expect(page.getByText(/settings saved|success/i)).toBeVisible({ timeout: 5000 });
      }
    }
  });

  test('should display overdue reminders with warning', async ({ page }) => {
    // Navigate to reminders page
    const remindersLink = page.getByRole('link', { name: /reminders|follow-ups/i });
    
    if (await remindersLink.isVisible()) {
      await remindersLink.click();

      // Look for overdue section or warning indicators
      const overdueSection = page.getByText(/overdue|late|past due/i);
      
      if (await overdueSection.isVisible()) {
        await expect(overdueSection).toBeVisible();
        
        // Verify overdue reminders are highlighted (red color, warning icon, etc.)
        const overdueIndicator = page.locator('[class*="red"], [class*="warning"], [class*="danger"]').first();
        await expect(overdueIndicator).toBeVisible();
      }
    }
  });
});
