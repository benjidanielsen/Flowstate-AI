import { NextFunction, Request, Response } from 'express';
import jwt, { JwtPayload, VerifyOptions } from 'jsonwebtoken';
import logger from '../utils/logger';
import { getSessionManager } from '../utils/sessionManager';

export const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey';
const JWT_AUDIENCE = process.env.JWT_AUDIENCE;
const JWT_ISSUER = process.env.JWT_ISSUER;

export interface AuthenticatedUser extends JwtPayload {
  sub: string;
  email?: string;
  role?: string;
  permissions?: string[];
  sessionId?: string;
  sid?: string;
}

declare global {
  namespace Express {
    // eslint-disable-next-line @typescript-eslint/naming-convention
    interface Request {
      user?: AuthenticatedUser;
    }
  }
}

const shouldValidateSession = (process.env.AUTH_VALIDATE_SESSION || 'true').toLowerCase() !== 'false';
const sessionManager = shouldValidateSession ? getSessionManager() : null;

function extractToken(req: Request): string | null {
  const authHeader = req.headers['authorization'];
  if (typeof authHeader === 'string' && authHeader.startsWith('Bearer ')) {
    return authHeader.slice(7);
  }

  if (req.query && typeof req.query.token === 'string') {
    return req.query.token;
  }

  return null;
}

function verifyToken(token: string): AuthenticatedUser {
  const verifyOptions: VerifyOptions = {
    algorithms: ['HS256'],
    audience: JWT_AUDIENCE || undefined,
    issuer: JWT_ISSUER || undefined,
  };

  const payload = jwt.verify(token, JWT_SECRET, verifyOptions) as AuthenticatedUser;
  if (!payload.sub) {
    throw new Error('Token payload missing subject');
  }

  return payload;
}

async function validateSessionIfNeeded(user: AuthenticatedUser): Promise<void> {
  if (!sessionManager) {
    return;
  }

  const sessionId = user.sessionId || user.sid;
  if (!sessionId) {
    return;
  }

  const session = await sessionManager.getSession(sessionId);
  if (!session) {
    throw new Error('Session not found or expired');
  }

  if (session.userId !== user.sub) {
    throw new Error('Session subject mismatch');
  }
}

export const authenticateToken = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const token = extractToken(req);

    if (!token) {
      logger.warn('Authentication failed: missing token', { path: req.path });
      res.status(401).json({ error: 'Authentication token is required' });
      return;
    }

    const user = verifyToken(token);
    await validateSessionIfNeeded(user);

    req.user = {
      ...user,
      role: user.role || 'user',
    };

    next();
  } catch (error: any) {
    logger.warn('Authentication failed', {
      message: error.message,
      path: req.path,
    });

    const status = error.name === 'TokenExpiredError' ? 401 : 403;
    res.status(status).json({ error: 'Invalid or expired authentication token' });
  }
};

export const optionalAuthentication = async (req: Request, _res: Response, next: NextFunction) => {
  try {
    const token = extractToken(req);
    if (!token) {
      next();
      return;
    }

    const user = verifyToken(token);
    await validateSessionIfNeeded(user);
    req.user = {
      ...user,
      role: user.role || 'user',
    };
  } catch (error) {
    logger.warn('Optional authentication failed', {
      message: (error as Error).message,
      path: req.path,
    });
  }

  next();
};
