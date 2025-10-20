import { NextFunction, Request, Response } from 'express';
import logger from '../utils/logger';
import { AuthenticatedUser } from './authMiddleware';

export const Roles = {
  ADMIN: 'admin',
  MANAGER: 'manager',
  ANALYST: 'analyst',
  AGENT: 'agent',
  INTEGRATION: 'integration',
  SERVICE: 'service',
  USER: 'user',
} as const;

export type Role = typeof Roles[keyof typeof Roles];

export const authorizeRoles = (...allowedRoles: Role[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = req.user as AuthenticatedUser | undefined;

    if (!user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    if (allowedRoles.length === 0) {
      next();
      return;
    }

    const role = (user.role || Roles.USER) as Role;
    if (!allowedRoles.includes(role)) {
      logger.warn('Authorization failed', {
        path: req.path,
        role,
        allowedRoles,
      });
      res.status(403).json({ error: 'Insufficient role permissions' });
      return;
    }

    next();
  };
};

export const authorizePermissions = (...requiredPermissions: string[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    const user = req.user as AuthenticatedUser | undefined;

    if (!user) {
      res.status(401).json({ error: 'Authentication required' });
      return;
    }

    const permissions = user.permissions || [];
    const missing = requiredPermissions.filter((permission) => !permissions.includes(permission));

    if (missing.length > 0) {
      logger.warn('Permission check failed', {
        path: req.path,
        role: user.role,
        missing,
      });
      res.status(403).json({ error: 'Missing required permissions', missing });
      return;
    }

    next();
  };
};
