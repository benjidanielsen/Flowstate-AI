import { request, Page, APIRequestContext } from '@playwright/test';

interface CredentialOptions {
  username: string;
  password: string;
}

interface AuthOptions {
  credentials?: CredentialOptions;
  apiBaseUrl?: string;
}

const DEFAULT_CREDENTIALS: CredentialOptions = {
  username: process.env.E2E_USERNAME ?? 'e2e-tester',
  password: process.env.E2E_PASSWORD ?? 'TestPassword!123',
};

const DEFAULT_API_BASE_URL = process.env.E2E_API_URL ?? 'http://localhost:3001';

async function withAuthRequestContext(apiBaseUrl: string): Promise<APIRequestContext> {
  return request.newContext({
    baseURL: apiBaseUrl,
    extraHTTPHeaders: {
      'Content-Type': 'application/json',
    },
  });
}

async function ensureTestUser(api: APIRequestContext, credentials: CredentialOptions): Promise<void> {
  const response = await api.post('/api/auth/register', { data: credentials });

  if (response.status() === 201 || response.status() === 409) {
    return;
  }

  const body = await response.text();
  throw new Error(`Failed to provision E2E user (${response.status()}): ${body}`);
}

async function acquireAuthToken(api: APIRequestContext, credentials: CredentialOptions): Promise<string> {
  const response = await api.post('/api/auth/login', { data: credentials });

  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Failed to log in E2E user (${response.status()}): ${body}`);
  }

  const payload = await response.json();
  if (!payload?.token || typeof payload.token !== 'string') {
    throw new Error('Login response did not include a token');
  }

  return payload.token;
}

export async function authenticateViaApi(page: Page, options?: AuthOptions): Promise<string> {
  const credentials = options?.credentials ?? DEFAULT_CREDENTIALS;
  const apiBaseUrl = options?.apiBaseUrl ?? DEFAULT_API_BASE_URL;

  const api = await withAuthRequestContext(apiBaseUrl);

  try {
    await ensureTestUser(api, credentials);
    const token = await acquireAuthToken(api, credentials);

    await page.context().addInitScript((storedToken) => {
      window.localStorage.setItem('token', storedToken as string);
    }, token);

    return token;
  } finally {
    await api.dispose();
  }
}

export async function prepareAuthenticatedPage(page: Page, path: string = '/'): Promise<void> {
  await authenticateViaApi(page);
  await page.goto('/login');
  await page.waitForLoadState('domcontentloaded');
  await page.evaluate(() => {
    if (!window.localStorage.getItem('token')) {
      throw new Error('Authentication token was not stored in localStorage');
    }
  });
  await page.goto(path);
  await page.waitForLoadState('networkidle');
  if (path.startsWith('/customers')) {
    await page.getByRole('button', { name: /add customer|new customer/i }).waitFor({ state: 'visible', timeout: 15000 });
  }
}
interface CustomerCreatePayload {
  name?: string;
  email?: string;
  phone?: string;
  status?: string;
  notes?: string;
  next_action?: string;
  next_action_date?: string;
  source?: string;
  country?: string;
  language?: string;
}

interface CustomerApiResponse {
  id: string;
  name: string;
  email?: string | null;
  phone?: string | null;
  status?: string | null;
  notes?: string | null;
  next_action?: string | null;
  next_action_date?: string | null;
  prospect_why?: string | null;
  country?: string | null;
  language?: string | null;
  source?: string | null;
  [key: string]: unknown;
}

export async function createCustomerViaApi(overrides?: CustomerCreatePayload, options?: AuthOptions): Promise<CustomerApiResponse> {
  const credentials = options?.credentials ?? DEFAULT_CREDENTIALS;
  const apiBaseUrl = options?.apiBaseUrl ?? DEFAULT_API_BASE_URL;

  const bootstrapContext = await withAuthRequestContext(apiBaseUrl);

  try {
    await ensureTestUser(bootstrapContext, credentials);
    const token = await acquireAuthToken(bootstrapContext, credentials);

    const authedContext = await request.newContext({
      baseURL: apiBaseUrl,
      extraHTTPHeaders: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
    });

    try {
      const payload = {
        name: overrides?.name ?? `E2E Customer ${Date.now()}`,
        email: overrides?.email,
        phone: overrides?.phone,
        status: overrides?.status ?? undefined,
        notes: overrides?.notes,
        next_action: overrides?.next_action,
        next_action_date: overrides?.next_action_date,
        source: overrides?.source,
        country: overrides?.country,
        language: overrides?.language,
      };

      const response = await authedContext.post('/api/customers', { data: payload });
      if (!response.ok()) {
        const body = await response.text();
        throw new Error(`Failed to create customer (${response.status()}): ${body}`);
      }

      const customer = await response.json();
      return customer as CustomerApiResponse;
    } finally {
      await authedContext.dispose();
    }
  } finally {
    await bootstrapContext.dispose();
  }
}

