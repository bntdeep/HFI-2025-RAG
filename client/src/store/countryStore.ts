import { create } from 'zustand';
import { apiClient } from '../api/client.js';
import type { CountryProfileResponse } from '../types/index.js';

interface CountryStore {
  selectedCountry: string;
  result: CountryProfileResponse | null;
  isLoading: boolean;
  error: string | null;
  setCountry(c: string): void;
  runProfile(): Promise<void>;
  reset(): void;
}

export const useCountryStore = create<CountryStore>((set, get) => ({
  selectedCountry: '',
  result: null,
  isLoading: false,
  error: null,

  setCountry: (c) => set({ selectedCountry: c }),

  runProfile: async () => {
    const { selectedCountry } = get();
    if (!selectedCountry) return;
    set({ isLoading: true, error: null });
    try {
      const result = await apiClient.profile(selectedCountry);
      set({ result, isLoading: false });
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  reset: () => set({ result: null, error: null }),
}));
