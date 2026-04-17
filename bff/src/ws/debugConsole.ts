import { WebSocketServer, WebSocket } from 'ws';
import type { IncomingMessage } from 'http';
import type { Server } from 'http';
import type { DebugEvent } from '../types/index.js';

const clients = new Set<WebSocket>();

export function attachDebugWebSocket(server: Server): void {
  const wss = new WebSocketServer({ server, path: '/ws/debug' });

  wss.on('connection', (ws: WebSocket, _req: IncomingMessage) => {
    clients.add(ws);
    ws.on('close', () => clients.delete(ws));
    ws.on('error', () => clients.delete(ws));
    ws.send(JSON.stringify({ type: 'connected', timestamp: Date.now() }));
  });
}

export function broadcastDebugEvents(events: DebugEvent[]): void {
  if (!events.length || !clients.size) return;
  const message = JSON.stringify({ type: 'debug_batch', events });
  for (const client of clients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  }
}

export function broadcastError(message: string): void {
  broadcastDebugEvents([{
    type: 'error',
    timestamp: Date.now(),
    payload: { message },
  }]);
}
