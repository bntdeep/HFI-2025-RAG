import { useEffect, useRef } from 'react';
import { useDebugStore } from '../store/debugStore.js';
import type { DebugEvent } from '../types/index.js';

export function useWebSocket() {
  const addEvents = useDebugStore(s => s.addEvents);
  const shouldReconnect = useRef(true);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    shouldReconnect.current = true;
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const url = `${protocol}//${window.location.host}/ws/debug`;

    const connect = () => {
      if (!shouldReconnect.current) return;
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onmessage = (e) => {
        try {
          const data = JSON.parse(e.data) as DebugEvent | DebugEvent[];
          addEvents(Array.isArray(data) ? data : [data]);
        } catch {
          // ignore malformed messages
        }
      };

      ws.onclose = () => {
        // reconnect after 3s only if not deliberately closed
        if (shouldReconnect.current) {
          setTimeout(connect, 3000);
        }
      };
    };

    connect();
    return () => {
      shouldReconnect.current = false;
      wsRef.current?.close();
    };
  }, [addEvents]);
}
