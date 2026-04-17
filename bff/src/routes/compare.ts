import { Router } from 'express';
import { pythonClient } from '../python/client.js';
import { COMPARE_SYSTEM_PROMPT } from '../prompts/compare.js';
import { broadcastDebugEvents } from '../ws/debugConsole.js';
import type { Message } from '../types/index.js';

const router = Router();

router.post('/', async (req, res, next) => {
  try {
    const { countries, params } = req.body as { countries: string[]; params?: string[] };

    if (!Array.isArray(countries) || countries.length < 2) {
      res.status(422).json({ error: 'At least 2 countries required' });
      return;
    }

    // Inject system prompt as the first history message
    const history: Message[] = [
      { role: 'system', content: COMPARE_SYSTEM_PROMPT },
    ];

    const result = await pythonClient.compare(countries, params ?? [], history);

    // Forward debug events to WebSocket clients (best-effort)
    const rawResult = result as unknown as Record<string, unknown>;
    broadcastDebugEvents((rawResult.debug_events as never[]) ?? []);

    res.json(result);
  } catch (err) {
    next(err);
  }
});

export default router;
