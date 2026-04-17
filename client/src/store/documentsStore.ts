import { create } from 'zustand';
import { apiClient } from '../api/client.js';
import type { DocumentRecord } from '../types/index.js';

interface DocumentsStore {
  documents: DocumentRecord[];
  isLoading: boolean;
  load(): Promise<void>;
  upload(file: File): Promise<void>;
  remove(id: string): Promise<void>;
}

export const useDocumentsStore = create<DocumentsStore>((set) => ({
  documents: [],
  isLoading: false,

  load: async () => {
    set({ isLoading: true });
    try {
      const documents = await apiClient.listDocuments();
      set({ documents, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  upload: async (file) => {
    await apiClient.uploadDocument(file);
    const documents = await apiClient.listDocuments();
    set({ documents });
  },

  remove: async (id) => {
    await apiClient.deleteDocument(id);
    set(s => ({ documents: s.documents.filter(d => d.id !== id) }));
  },
}));
