import axios, { AxiosInstance } from 'axios';
import FormData from 'form-data';
import type {
  CompareResponse,
  CountryProfileResponse,
  ChatResponse,
  DocumentRecord,
  Message,
} from '../types/index.js';

const py: AxiosInstance = axios.create({
  baseURL: process.env.PYTHON_URL ?? 'http://localhost:8080',
  timeout: 300_000,  // LLM calls can take 2-3 minutes
});

export const pythonClient = {
  health: (): Promise<{ status: string }> =>
    py.get('/api/health').then(r => r.data),

  compare: (
    countries: string[],
    params: string[],
    history: Message[],
  ): Promise<CompareResponse> =>
    py.post('/api/compare', { countries, params, history }).then(r => r.data),

  profile: (country: string): Promise<CountryProfileResponse> =>
    py.get(`/api/profile/${encodeURIComponent(country)}`).then(r => r.data),

  chat: (message: string, history: Message[]): Promise<ChatResponse> =>
    py.post('/api/chat', { message, history }).then(r => r.data),

  listDocuments: (): Promise<DocumentRecord[]> =>
    py.get('/api/documents').then(r => r.data),

  uploadDocument: (form: FormData): Promise<unknown> =>
    py.post('/api/documents', form, {
      headers: form.getHeaders(),
    }).then(r => r.data),

  deleteDocument: (id: string): Promise<{ deleted: boolean; chunks_removed: number }> =>
    py.delete(`/api/documents/${encodeURIComponent(id)}`).then(r => r.data),

  countries: (): Promise<unknown[]> =>
    py.get('/api/countries').then(r => r.data),

  parameters: (): Promise<unknown[]> =>
    py.get('/api/parameters').then(r => r.data),
};
