import axios from 'axios';

// Base URL configurada para el backend FastAPI (puerto 8090 por defecto)
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8090';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,
});

export interface PredictionResponse {
  label: 'ham' | 'spam';
  spam_probability: number;
  ham_probability: number;
  risk_level: 'BAJO' | 'MEDIO' | 'CRÍTICO';
  latency_ms: number;
  detected_tokens: string[];
  text?: string;
}

export interface BatchSummary {
  total: number;
  spam_count: number;
  ham_count: number;
  spam_percentage: number;
  avg_latency_ms: number;
}

export interface BatchResponse {
  summary: BatchSummary;
  total_latency_ms: number;
  predictions: PredictionResponse[];
}

export interface TFIDFFeatureWeight {
  feature: string;
  weight: number;
}

export interface NLPDebugResponse {
  original: string;
  normalized: string;
  tokens: string[];
  no_stopwords: string[];
  stemmed_or_lemmatized: string[];
  tfidf_top_features: TFIDFFeatureWeight[];
}

export interface ConfusionMatrixData {
  tn: number;
  fp: number;
  fn: number;
  tp: number;
  matrix: number[][];
}

export interface ClassMetric {
  precision: number;
  recall: number;
  f1_score: number;
  support: number;
}

export interface ModelBenchmarkItem {
  model_name: string;
  confusion_matrix: ConfusionMatrixData;
  rates: {
    false_positive_rate: number;
    false_negative_rate: number;
  };
  class_metrics: {
    ham: ClassMetric;
    spam: ClassMetric;
  };
  aggregate_metrics: {
    accuracy: number;
    f1_macro: number;
    f1_weighted: number;
  };
  training_duration_seconds: number;
}

export interface MetricsResponse {
  timestamp: string;
  winner_model: string;
  hyperparameter_tuning: {
    best_nb_alpha?: number;
    best_nb_f1?: number;
    nb_cv_grid?: Record<string, number>;
    best_lr_c?: number;
    best_lr_f1?: number;
    lr_cv_grid?: Record<string, number>;
    [key: string]: unknown;
  };
  benchmark_summary: ModelBenchmarkItem[];
}

export interface MessageAuditRecord {
  id: number;
  created_at: string;
  message_text: string;
  prediction: string;
  probability_spam: number;
  probability_ham: number;
  risk_level: string;
  detected_tokens: string[];
  latency_ms: number;
}

export interface HistoryResponse {
  total: number;
  limit: number;
  offset: number;
  records: MessageAuditRecord[];
}

export interface HealthResponse {
  status: string;
  model_loaded: boolean;
  model_name: string;
  version: string;
  timestamp: string;
  database_connected: boolean;
}

export const checkHealth = async (): Promise<HealthResponse> => {
  const { data } = await apiClient.get<HealthResponse>('/health');
  return data;
};

export const predictMessage = async (text: string): Promise<PredictionResponse> => {
  const { data } = await apiClient.post<PredictionResponse>('/predict', { text });
  return data;
};

export const predictBatchCsv = async (file: File): Promise<BatchResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await apiClient.post<BatchResponse>('/predict/batch/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return data;
};

export const predictBatchJson = async (messages: string[]): Promise<BatchResponse> => {
  const payload = { messages: messages.map((text) => ({ text })) };
  const { data } = await apiClient.post<BatchResponse>('/predict/batch', payload);
  return data;
};

export const debugNLP = async (text: string): Promise<NLPDebugResponse> => {
  const { data } = await apiClient.post<NLPDebugResponse>('/nlp/debug', { text });
  return data;
};

export const getMetrics = async (): Promise<MetricsResponse> => {
  const { data } = await apiClient.get<MetricsResponse>('/metrics');
  return data;
};

export const getHistory = async (limit: number = 10, offset: number = 0): Promise<HistoryResponse> => {
  const { data } = await apiClient.get<HistoryResponse>('/history', {
    params: { limit, offset },
  });
  return data;
};
