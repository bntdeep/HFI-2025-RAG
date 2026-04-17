import { Router } from 'express';
import { pythonClient } from '../python/client.js';

const router = Router();

router.get('/', async (_req, res, next) => {
  try {
    const pyHealth = await pythonClient.health();
    res.json({ status: 'ok', python: pyHealth.status });
  } catch {
    res.status(503).json({ status: 'degraded', python: 'unreachable' });
  }
});

export default router;
