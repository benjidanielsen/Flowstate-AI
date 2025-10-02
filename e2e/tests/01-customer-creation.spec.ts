import { test, expect } from '@playwright/test';

/**
 * E2E Test: Customer Creation Flow
 * 
 * Tests the complete customer creation workflow in the FlowState-AI CRM system.
 * Verifies that customers can be created with all required fields and appear in the system.
 * 
 * Author: Manus 7
 * Task: TASK-110 (End-to-End Testing)
 */

test.describe('Customer Creation Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('/');
    
    // Wait for the application to load
    await page.waitForLoadState('networkidle');
  });

  test('should create a new customer with all required fields', async ({ page }) => {
    // Click on "Add Customer" or "New Customer" button
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    // Fill in customer details
    await page.getByLabel(/name/i).fill('John Doe');
    await page.getByLabel(/email/i).fill('john.doe@example.com');
    await page.getByLabel(/phone/i).fill('+1234567890');
    
    // Submit the form
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Verify success message appears
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Verify customer appears in the list
    await expect(page.getByText('John Doe')).toBeVisible();
    await expect(page.getByText('john.doe@example.com')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    // Click on "Add Customer" button
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    // Try to submit without filling required fields
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Verify validation errors appear
    await expect(page.getByText(/name is required|required field/i)).toBeVisible();
  });

  test('should create customer with default pipeline status', async ({ page }) => {
    // Create a new customer
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('Jane Smith');
    await page.getByLabel(/email/i).fill('jane.smith@example.com');
    
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for success
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Click on the customer to view details
    await page.getByText('Jane Smith').click();

    // Verify default status is "New Lead" or "Lead"
    await expect(page.getByText(/new lead|lead/i)).toBeVisible();
  });

  test('should display customer in the customer list', async ({ page }) => {
    // Create a new customer
    const addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    const uniqueEmail = `test-${Date.now()}@example.com`;
    await page.getByLabel(/name/i).fill('Test Customer');
    await page.getByLabel(/email/i).fill(uniqueEmail);
    
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for success
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Verify customer appears in the list with unique email
    await expect(page.getByText(uniqueEmail)).toBeVisible();
  });

  test('should prevent duplicate email addresses', async ({ page }) => {
    const duplicateEmail = 'duplicate@example.com';

    // Create first customer
    let addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('First Customer');
    await page.getByLabel(/email/i).fill(duplicateEmail);
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Wait for success
    await expect(page.getByText(/customer created|success/i)).toBeVisible({ timeout: 5000 });

    // Try to create second customer with same email
    addCustomerButton = page.getByRole('button', { name: /add customer|new customer/i });
    await addCustomerButton.click();

    await page.getByLabel(/name/i).fill('Second Customer');
    await page.getByLabel(/email/i).fill(duplicateEmail);
    await page.getByRole('button', { name: /save|create|submit/i }).click();

    // Verify error message appears
    await expect(page.getByText(/email already exists|duplicate email/i)).toBeVisible({ timeout: 5000 });
  });
});
