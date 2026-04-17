import { create } from 'zustand';
import type { DebugEvent } from '../types/index.js';

interface DebugStore {
  events: DebugEvent[];
  isOpen: boolean;
  addEvents(events: DebugEvent[]): void;
  toggle(): void;
  clear(): void;
}

export const useDebugStore = create<DebugStore>((set) => ({
  events: [],
  isOpen: false,

  addEvents: (events) =>
    set(s => ({ events: [...s.events, ...events].slice(-500) })),  // cap at 500

  toggle: () => set(s => ({ isOpen: !s.isOpen })),

  clear: () => set({ events: [] }),
}));
