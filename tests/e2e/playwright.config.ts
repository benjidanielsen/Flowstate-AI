import { defineConfig } from '@playwright/test';

export default defineConfig({
  timeout: 30_000,
  use: {
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:8080',
  },
});
