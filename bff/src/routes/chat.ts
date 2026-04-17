import { Router } from 'express';
import { pythonClient } from '../python/client.js';
import { CHAT_SYSTEM_PROMPT } from '../prompts/chat.js';
import { broadcastDebugEvents } from '../ws/debugConsole.js';
import type { Message } from '../types/index.js';

const router = Router();

router.post('/', async (req, res, next) => {
  try {
    const { message, history = [] } = req.body as { message?: string; history?: Message[] };

    if (!message) {
      res.status(422).json({ error: 'message is required' });
      return;
    }

    // Prepend system prompt to history if not already present
    const fullHistory: Message[] = history[0]?.role === 'system'
      ? history
      : [{ role: 'system', content: CHAT_SYSTEM_PROMPT }, ...history];

    const result = await pythonClient.chat(message, fullHistory);

    const rawResult = result as unknown as Record<string, unknown>;
    broadcastDebugEvents((rawResult.debug_events as never[]) ?? []);

    res.json(result);
  } catch (err) {
    next(err);
  }
});

export default router;
