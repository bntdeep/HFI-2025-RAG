import { create } from 'zustand';
import { apiClient } from '../api/client.js';
import type { ChatResponse, Message } from '../types/index.js';

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  chartConfig?: ChatResponse['chart_config'];
  sources?: ChatResponse['sources'];
}

interface ChatStore {
  messages: ChatMessage[];
  history: Message[];
  isLoading: boolean;
  error: string | null;
  sendMessage(text: string): Promise<void>;
  clearChat(): void;
}

export const useChatStore = create<ChatStore>((set, get) => ({
  messages: [],
  history: [],
  isLoading: false,
  error: null,

  sendMessage: async (text: string) => {
    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: 'user', content: text };
    set(s => ({
      messages: [...s.messages, userMsg],
      history: [...s.history, { role: 'user', content: text }],
      isLoading: true,
      error: null,
    }));

    try {
      const result = await apiClient.chat(text, get().history);
      const assistantMsg: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: result.response_text,
        chartConfig: result.chart_config ?? undefined,
        sources: result.sources,
      };
      set(s => ({
        messages: [...s.messages, assistantMsg],
        history: [...s.history, { role: 'assistant', content: result.response_text }],
        isLoading: false,
      }));
    } catch (e) {
      set({ error: String(e), isLoading: false });
    }
  },

  clearChat: () => set({ messages: [], history: [], error: null }),
}));
