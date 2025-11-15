import { Request, Response, NextFunction } from 'express';
import jwt, { JwtPayload } from 'jsonwebtoken';
import { safeLogger } from '../utils/piiRedaction';

interface AuthenticatedUser extends JwtPayload {
  id: string;
  username?: string;
  roles?: string[];
  provider?: string;
  role?: string;
}

interface OAuthProviderConfig {
  name: string;
  issuer?: string;
  audience?: string;
}

const baselineRoles = (process.env.RBAC_BASELINE_ROLES || 'agent')
  .split(',')
  .map(role => role.trim())
  .filter(Boolean);

const oauthProviders: Record<string, OAuthProviderConfig> = (() => {
  if (!process.env.OAUTH_PROVIDERS) {
    return {};
  }
  try {
    const parsed = JSON.parse(process.env.OAUTH_PROVIDERS);
    if (Array.isArray(parsed)) {
      return parsed.reduce((acc, provider) => {
        if (provider?.name) {
          acc[provider.name] = provider;
        }
        return acc;
      }, {} as Record<string, OAuthProviderConfig>);
    }
    return parsed;
  } catch (error) {
    safeLogger.warn('Failed to parse OAUTH_PROVIDERS; falling back to internal auth only', error);
    return {};
  }
})();

const buildSecretChain = (): string[] => {
  const secrets = [
    process.env.JWT_SECRET_CURRENT,
    process.env.JWT_SECRET,
    process.env.JWT_SECRET_PREVIOUS,
  ];
  if (process.env.JWT_SECRET_CHAIN) {
    secrets.push(...process.env.JWT_SECRET_CHAIN.split(',').map(s => s.trim()));
  }
  const filtered = Array.from(new Set(secrets.filter(Boolean))) as string[];
  if (!filtered.length) {
    safeLogger.warn('No JWT secrets provided; using insecure fallback for development');
    filtered.push('supersecretjwtkey');
  }
  return filtered;
};

let secretChain = buildSecretChain();

const rotateSecretsIfNeeded = () => {
  if (process.env.JWT_SECRET_ROTATION === 'true') {
    secretChain = buildSecretChain();
  }
};

export const getActiveJwtSecret = (): string => {
  rotateSecretsIfNeeded();
  return secretChain[0];
};

const verifyWithChain = (token: string): AuthenticatedUser | null => {
  rotateSecretsIfNeeded();
  let lastError: Error | null = null;
  for (const secret of secretChain) {
    try {
      return jwt.verify(token, secret) as AuthenticatedUser;
    } catch (error) {
      lastError = error as Error;
    }
  }
  if (lastError) {
    safeLogger.warn('JWT verification failed for all secrets', { message: lastError.message });
  }
  return null;
};

const ensureBaselineRole = (roles: string[] | undefined): boolean => {
  if (!baselineRoles.length) {
    return true;
  }
  const normalized = roles || [];
  return baselineRoles.some(role => normalized.includes(role));
};

const validateOAuthProvider = (user: AuthenticatedUser): boolean => {
  const providerName = (user.provider as string) || undefined;
  if (!providerName) {
    return true;
  }
  const provider = oauthProviders[providerName];
  if (!provider) {
    safeLogger.warn('OAuth provider not allowed', { provider: providerName });
    return false;
  }
  if (provider.issuer && user.iss && user.iss !== provider.issuer) {
    safeLogger.warn('OAuth issuer mismatch', { provider: providerName, issuer: user.iss });
    return false;
  }
  if (provider.audience && user.aud && user.aud !== provider.audience) {
    safeLogger.warn('OAuth audience mismatch', { provider: providerName, audience: user.aud });
    return false;
  }
  return true;
};

export const authenticateToken = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (!token) {
    safeLogger.warn('Missing bearer token', { path: req.path });
    return res.sendStatus(401);
  }

  const decoded = verifyWithChain(token);
  if (!decoded) {
    safeLogger.warn('Token verification failed', { path: req.path });
    return res.sendStatus(403);
  }

  if (!validateOAuthProvider(decoded)) {
    return res.sendStatus(403);
  }

  const roles = Array.isArray(decoded.roles) && decoded.roles.length
    ? decoded.roles
    : [decoded.role as string].filter(Boolean);
  decoded.roles = roles.length ? roles : [process.env.RBAC_FALLBACK_ROLE || 'agent'];

  if (!ensureBaselineRole(decoded.roles)) {
    safeLogger.warn('RBAC baseline check failed', { userId: decoded.id, roles: decoded.roles });
    return res.sendStatus(403);
  }

  (req as any).user = decoded;
  safeLogger.info('Authenticated request', { userId: decoded.id, path: req.path, provider: decoded.provider || 'internal' });
  next();
};

export const authorizeRoles = (...allowedRoles: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = (req as any).user as AuthenticatedUser | undefined;
    if (!user) {
      return res.sendStatus(401);
    }
    if (allowedRoles.length && !allowedRoles.some(role => user.roles?.includes(role))) {
      safeLogger.warn('Route RBAC check failed', { userId: user.id, path: req.path, required: allowedRoles });
      return res.sendStatus(403);
    }
    next();
  };
};
