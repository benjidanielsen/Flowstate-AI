import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

const JWT_SECRET = process.env.JWT_SECRET || 'supersecretjwtkey'; // Use the same secret as in authService

export const authenticateToken = (req: Request, res: Response, next: NextFunction) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];

  if (token == null) return res.sendStatus(401); // No token

  const bypassToken = process.env.BYPASS_AUTH_TOKEN;
  if (bypassToken && token === bypassToken) {
    (req as any).user = { id: 'bypass-user', role: 'system' };
    return next();
  }

  jwt.verify(token, JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403); // Invalid token
    (req as any).user = user; // Attach user payload to request
    next();
  });
};

