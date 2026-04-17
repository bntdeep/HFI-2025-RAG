import { create } from 'zustand';
import { apiClient } from '../api/client.js';
import { DEFAULT_COMPARE_PARAMS } from '../constants.js';
import type { CompareResponse } from '../types/index.js';

interface CompareStore {
  countryA: string;
  countryB: string;
  selectedParams: string[];
  result: CompareResponse | null;
  isLoading: boolean;
  error: string | null;
  setCountryA(c: string): void;
  setCountryB(c: string): void;
  toggleParam(p: string): void;
  runCompare(): Promise<void>;
  reset(): void;
}

export const useCompareStore = create<CompareStore>((set, get) => ({
  countryA: '',
  countryB: '',
  selectedParams: [...DEFAULT_COMPARE_PARAMS],
  result: null,
  isLoading: false,
  error: null,

  setCountryA: (c) => set({ countryA: c }),
  setCountryB: (c) => set({ countryB: c }),

  toggleParam: (p) =>
    set(s => ({
      selectedParams: s.selectedParams.includes(p)
        ? s.selectedParams.filter(x => x !== p)
        : [...s.selectedParams, p],
    })),

  runCompare: async () => {
    const { countryA, countryB, selectedParams } = get();
    if (!countryA || !countryB) return;
    set({ isLoading: true, error: null });
    try {
      const result = await apiClient.compare([countryA, countryB], selectedParams);
      set({ result, isLoading: false });
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  reset: () => set({ result: null, error: null }),
}));
