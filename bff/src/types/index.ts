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
}

export interface ChatResponse {
  response_text: string;
  chart_config: ChartConfig | null;
  sources: SourceRef[];
}

export interface ChartConfig {
  chart_type: 'bar' | 'pie' | 'line' | 'radar' | 'scatter';
  title: string;
  data: Record<string, unknown>[];
  x_key: string;
  y_keys: string[];
  colors: string[] | null;
}

export interface DocumentRecord {
  id: string;
  name: string;
  path: string;
  total_chunks: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DebugEvent {
  type: 'mcp_call' | 'retrieval' | 'llm_request' | 'llm_response' | 'chart_ready' | 'error' | string;
  timestamp: number;
  payload: unknown;
}

export interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
}
