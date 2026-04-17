export interface SourceRef {
  page_number: number;
  section: string;
  relevance_score: number;
  document_name: string;
}

export interface ButterflyRow {
  param: string;
  country_a: number;
  country_b: number;
}

export interface CompareResponse {
  countries: string[];
  params: string[];
  butterfly_data: ButterflyRow[];
  scores_matrix: Record<string, Record<string, number>>;
  response_text: string;
  sources: SourceRef[];
  debug_events?: unknown[];
}

export interface CountryProfileResponse {
  name: string;
  flag: string;
  overall_rank: number;
  overall_score: number;
  personal_freedom_score: number;
  economic_freedom_score: number;
  rule_of_law: number | null;
  security: number | null;
  movement: number | null;
  religion: number | null;
  expression: number | null;
  association: number | null;
  subcategories: Record<string, number>;
  strengths: string[];
  weaknesses: string[];
  response_text: string;
  sources: SourceRef[];
  debug_events?: unknown[];
}

export interface ChartConfig {
  chart_type: 'radar' | 'bar' | 'line' | 'butterfly';
  title?: string;
  data?: unknown[];
  x_key?: string;
  y_keys?: string[];
  butterfly_data?: ButterflyRow[];
}

export interface ChatResponse {
  response_text: string;
  chart_config: ChartConfig | null;
  sources: SourceRef[];
  debug_events?: unknown[];
}

export interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface DocumentRecord {
  id: string;
  name: string;
  pages: number;
  chunks: number;
  status: string;
}

export interface DebugEvent {
  type: string;
  node?: string;
  message?: string;
  timestamp?: string;
  data?: unknown;
}
