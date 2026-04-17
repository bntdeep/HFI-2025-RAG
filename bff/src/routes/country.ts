import { Router } from 'express';
import { pythonClient } from '../python/client.js';
import { COUNTRY_SYSTEM_PROMPT } from '../prompts/country.js';
import { broadcastDebugEvents } from '../ws/debugConsole.js';

const router = Router();

// POST /api/country  { country: string }
router.post('/', async (req, res, next) => {
  try {
    const { country } = req.body as { country?: string };

    if (!country) {
      res.status(422).json({ error: 'country is required' });
      return;
    }

    // The system prompt is currently embedded in the Python profile endpoint prompt.
    // We surface it here for visibility and future customisation.
    // (Python /api/profile does not accept history yet; this is a no-op stub.)
    void COUNTRY_SYSTEM_PROMPT;

    const result = await pythonClient.profile(country);

    const rawResult = result as unknown as Record<string, unknown>;
    broadcastDebugEvents((rawResult.debug_events as never[]) ?? []);

    res.json(result);
  } catch (err) {
    next(err);
  }
});

export default router;
