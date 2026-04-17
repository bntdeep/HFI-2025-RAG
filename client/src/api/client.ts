import axios from 'axios';
import type {
  CompareResponse,
  CountryProfileResponse,
  ChatResponse,
  DocumentRecord,
  Message,
} from '../types/index.js';

const api = axios.create({ baseURL: '/api', timeout: 120_000 });

export const apiClient = {
  compare(countries: string[], params: string[]): Promise<CompareResponse> {
    return api.post('/compare', { countries, params }).then(r => r.data);
  },

  profile(country: string): Promise<CountryProfileResponse> {
    return api.post('/country', { country }).then(r => r.data);
  },

  chat(message: string, history: Message[]): Promise<ChatResponse> {
    return api.post('/chat', { message, history }).then(r => r.data);
  },

  listDocuments(): Promise<DocumentRecord[]> {
    return api.get('/documents').then(r => r.data);
  },

  uploadDocument(file: File): Promise<{ id: string; message: string }> {
    const form = new FormData();
    form.append('file', file);
    return api.post('/documents', form).then(r => r.data);
  },

  deleteDocument(id: string): Promise<{ message: string }> {
    return api.delete(`/documents/${id}`).then(r => r.data);
  },

  countries(): Promise<string[]> {
    return api.get('/countries').then(r => r.data);
  },

  parameters(): Promise<{ code: string; name: string; parent: string | null }[]> {
    return api.get('/parameters').then(r => r.data);
  },
};
