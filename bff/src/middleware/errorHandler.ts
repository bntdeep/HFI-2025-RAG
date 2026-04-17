import type { Request, Response, NextFunction } from 'express';

export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction,
): void {
  const message = err instanceof Error ? err.message : String(err);
  console.error('[BFF error]', message);
  res.status(500).json({ error: message });
}
