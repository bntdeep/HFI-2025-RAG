import { create } from 'zustand';
import { apiClient } from '../api/client.js';

interface MetaStore {
  countries: string[];
  parameters: { code: string; name: string; parent: string | null }[];
  loaded: boolean;
  load(): Promise<void>;
}

export const useMetaStore = create<MetaStore>((set, get) => ({
  countries: [],
  parameters: [],
  loaded: false,

  load: async () => {
    if (get().loaded) return;
    try {
      const [raw, parameters] = await Promise.all([
        apiClient.countries(),
        apiClient.parameters(),
      ]);
      // API returns either string[] or {name, ...}[] — normalize to string[]
      const countries = (raw as unknown[])
        .map((c) => (typeof c === 'string' ? c : (c as { name: string }).name))
        .sort((a, b) => a.localeCompare(b));
      set({ countries, parameters, loaded: true });
    } catch {
      // non-fatal — UI will handle empty lists
    }
  },
}));
