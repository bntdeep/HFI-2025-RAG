import { Router } from 'express';
import { pythonClient } from '../python/client.js';

const router = Router();

router.get('/countries', async (_req, res, next) => {
  try {
    res.json(await pythonClient.countries());
  } catch (err) {
    next(err);
  }
});

router.get('/parameters', async (_req, res, next) => {
  try {
    res.json(await pythonClient.parameters());
  } catch (err) {
    next(err);
  }
});

export default router;
