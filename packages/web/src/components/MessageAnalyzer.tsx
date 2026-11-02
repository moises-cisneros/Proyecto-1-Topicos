import React, { useEffect, useState } from 'react';
import { PredictionResponse, predictMessage } from '../services/api';
import { BatchAnalyzer } from './BatchAnalyzer';
import {
  AlertTriangle,
  CheckCircle,
  CheckCircle2,
  FileSpreadsheet,
  MessageSquare,
  Shield,
  Sliders,
  Sparkles,
  ThumbsDown,
  ThumbsUp,
  Trash2,
} from 'lucide-react';
import { Card } from './ui/Card';
import { Button } from './ui/Button';
import { Badge } from './ui/Badge';
import sampleData from '@resources/example/samples.json';

interface SampleItem {
  id: string;
  type: string;
  label: string;
  category: string;
  text: string;
}

interface MessageAnalyzerProps {
  onAnalyzeSuccess?: (text: string, result: PredictionResponse) => void;
  onInspectBatchMessage?: (text: string) => void;
  externalText?: string;
}

export const MessageAnalyzer: React.FC<MessageAnalyzerProps> = ({
  onAnalyzeSuccess,
  onInspectBatchMessage,
  externalText,
}) => {
  const [analysisMode, setAnalysisMode] = useState<'single' | 'batch'>(() => {
    const saved = localStorage.getItem('sms_sentinel_analysis_mode');
    return saved === 'batch' ? 'batch' : 'single';
  });

  const [text, setText] = useState<string>(() => {
    return localStorage.getItem('sms_sentinel_input_text') || '';
  });

  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const [result, setResult] = useState<PredictionResponse | null>(() => {
    try {
      const saved = localStorage.getItem('sms_sentinel_last_result');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [threshold, setThreshold] = useState<number>(() => {
    const saved = localStorage.getItem('sms_sentinel_threshold');
    if (saved) {
      const parsed = parseFloat(saved);
      if (!isNaN(parsed) && parsed >= 0.2 && parsed <= 0.8) {
        return parsed;
      }
    }
    return 0.5;
  });

  const [feedbackStatus, setFeedbackStatus] = useState<'correct' | 'corrected' | null>(() => {
    const saved = localStorage.getItem('sms_sentinel_feedback_status');
    return saved === 'correct' || saved === 'corrected' ? saved : null;
  });

  const [correctedLabel, setCorrectedLabel] = useState<string | null>(() => {
    return localStorage.getItem('sms_sentinel_corrected_label') || null;
  });

  useEffect(() => {
    localStorage.setItem('sms_sentinel_analysis_mode', analysisMode);
  }, [analysisMode]);

  useEffect(() => {
    localStorage.setItem('sms_sentinel_threshold', threshold.toString());
  }, [threshold]);

  useEffect(() => {
    if (text) {
      localStorage.setItem('sms_sentinel_input_text', text);
    } else {
      localStorage.removeItem('sms_sentinel_input_text');
    }
  }, [text]);

  useEffect(() => {
    if (result) {
      try {
        localStorage.setItem('sms_sentinel_last_result', JSON.stringify(result));
      } catch {
        // Fallback for storage limits
      }
    } else {
      localStorage.removeItem('sms_sentinel_last_result');
    }
  }, [result]);

  useEffect(() => {
    if (feedbackStatus) {
      localStorage.setItem('sms_sentinel_feedback_status', feedbackStatus);
    } else {
      localStorage.removeItem('sms_sentinel_feedback_status');
    }
  }, [feedbackStatus]);

  useEffect(() => {
    if (correctedLabel) {
      localStorage.setItem('sms_sentinel_corrected_label', correctedLabel);
    } else {
      localStorage.removeItem('sms_sentinel_corrected_label');
    }
  }, [correctedLabel]);

  useEffect(() => {
    if (externalText && externalText.trim()) {
      setText(externalText);
      setAnalysisMode('single');
      setError(null);
    }
  }, [externalText]);

  const charCount = text.length;
  const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
  const smsSegments = Math.ceil(charCount / 160) || 1;

  const handleClear = () => {
    setText('');
    setError(null);
    setResult(null);
    setFeedbackStatus(null);
    setCorrectedLabel(null);
    localStorage.removeItem('sms_sentinel_input_text');
    localStorage.removeItem('sms_sentinel_last_result');
    localStorage.removeItem('sms_sentinel_feedback_status');
    localStorage.removeItem('sms_sentinel_corrected_label');
  };

  const handleInspectFromBatch = (batchMsg: string) => {
    setText(batchMsg);
    setAnalysisMode('single');
    setError(null);
    if (onInspectBatchMessage) {
      onInspectBatchMessage(batchMsg);
    }
  };

  const handleLoadSample = (type: 'ham' | 'spam') => {
    const samples = (sampleData.samples || []) as SampleItem[];
    const matching = samples.filter((s: SampleItem) => s.type === type);
    if (matching.length > 0) {
      const selected = matching[Math.floor(Math.random() * matching.length)];
      setText(selected.text);
      setError(null);
    }
  };

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanText = text.trim();
    if (!cleanText) {
      setError('Por favor, ingrese un mensaje de texto para ejecutar el análisis.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);
    setFeedbackStatus(null);
    setCorrectedLabel(null);

    try {
      const response = await predictMessage(cleanText);
      setResult(response);
      if (onAnalyzeSuccess) {
        onAnalyzeSuccess(cleanText, response);
      }
    } catch (err: unknown) {
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axErr = err as {
          response?: {
            status?: number;
            data?: { detail?: string | Array<{ msg?: string; loc?: (string | number)[] }> | Record<string, unknown> };
          };
          message?: string;
        };
        const status = axErr.response?.status;
        const detail = axErr.response?.data?.detail;

        if (typeof detail === 'string') {
          setError(detail);
        } else if (Array.isArray(detail) && detail.length > 0) {
          const messages = detail
            .map((item) => {
              if (typeof item === 'object' && item !== null && 'msg' in item) {
                return item.msg;
              }
              return String(item);
            })
            .filter(Boolean)
            .join(' | ');
          setError(messages || 'El contenido del mensaje no cumple con los requisitos de validación.');
        } else if (status === 404) {
          setError('El servicio de inferencia no fue encontrado (HTTP 404). Verifique que el backend esté en ejecución.');
        } else if (status === 503) {
          setError('El modelo de detección no se encuentra disponible en este momento (HTTP 503).');
        } else if (status && status >= 500) {
          setError('Error interno en el servidor de inferencia. Por favor, intente nuevamente.');
        } else {
          setError(axErr.message || 'No fue posible completar el análisis del mensaje.');
        }
      } else if (typeof err === 'object' && err !== null && 'message' in err) {
        const standardErr = err as { message: string };
        setError(standardErr.message || 'No fue posible conectar con el servidor.');
      } else {
        setError('El servicio de análisis no está disponible temporalmente. Verifique la conexión con el servidor.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = (type: 'confirm' | 'invert') => {
    if (!result) return;
    if (type === 'confirm') {
      setFeedbackStatus('correct');
    } else {
      const current = correctedLabel ? correctedLabel : (rawSpamProb >= threshold ? 'spam' : 'ham');
      const inverted = current === 'spam' ? 'ham' : 'spam';
      setCorrectedLabel(inverted);
      setFeedbackStatus('corrected');
    }
  };

  const rawSpamProb = result ? result.spam_probability : 0.0;
  const initialIsSpam = result ? rawSpamProb >= threshold : false;
  const simulatedIsSpam = correctedLabel ? correctedLabel === 'spam' : initialIsSpam;
  const spamPercentage = (rawSpamProb * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Selector de Modo de Escaneo */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b app-border pb-3">
        <div className="flex items-center gap-2">
          <Button
            variant={analysisMode === 'single' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setAnalysisMode('single')}
            icon={<MessageSquare className="w-3.5 h-3.5" />}
          >
            Escáner Individual
          </Button>
          <Button
            variant={analysisMode === 'batch' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setAnalysisMode('batch')}
            icon={<FileSpreadsheet className="w-3.5 h-3.5" />}
          >
            Auditoría Masiva (.CSV)
          </Button>
        </div>

        {analysisMode === 'single' && (
          <div className="flex items-center gap-2 text-xs font-mono app-text-secondary app-card-subtle px-3 py-1.5 rounded-lg border app-border">
            <Sliders className="w-3.5 h-3.5 text-[#4361ee]" />
            <span>Sensibilidad del Umbral:</span>
            <input
              type="range"
              min="0.20"
              max="0.80"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-24 accent-[#4361ee] cursor-pointer"
            />
            <span className="font-bold app-text-primary">{(threshold * 100).toFixed(0)}%</span>
            <span className="text-[10px] app-text-muted">
              ({threshold <= 0.35 ? 'Alta' : threshold >= 0.65 ? 'Conservador' : 'Balanceado'})
            </span>
          </div>
        )}
      </div>

      {analysisMode === 'batch' ? (
        <BatchAnalyzer onInspectMessage={handleInspectFromBatch} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Panel de Ingesta */}
          <Card className="lg:col-span-7 p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <label htmlFor="smsInput" className="text-sm font-semibold app-text-primary">
                Mensaje SMS a Examinar:
              </label>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleLoadSample('ham')}
                >
                  Cargar Legítimo
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => handleLoadSample('spam')}
                >
                  Cargar Amenaza
                </Button>
              </div>
            </div>

            <textarea
              id="smsInput"
              rows={4}
              value={text}
              onChange={(e) => {
                setText(e.target.value);
                if (error) setError(null);
              }}
              className="w-full app-card-subtle border app-border rounded-lg p-3 app-text-primary font-sans text-sm focus:outline-none focus:border-[#4361ee]"
              placeholder="Pegue o escriba aquí el contenido del mensaje SMS..."
            />

            <div className="flex items-center justify-between text-xs app-text-secondary font-mono border-t app-border pt-3">
              <span>
                Longitud: {charCount} / 160 ({smsSegments} segmento{smsSegments > 1 ? 's' : ''}) | {wordCount} palabras
              </span>
              <button
                type="button"
                onClick={handleClear}
                className="app-text-muted hover:app-text-primary flex items-center gap-1 cursor-pointer"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Limpiar
              </button>
            </div>

            {error && (
              <Card variant="subtle" className="p-3 border-[#ef233c] text-[#ef233c] text-xs font-mono flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 shrink-0" />
                <span>{error}</span>
              </Card>
            )}

            <div className="pt-2">
              <Button
                variant="primary"
                size="md"
                disabled={loading}
                onClick={() => handleAnalyze()}
                className="w-full"
                icon={<Sparkles className="w-4 h-4" />}
              >
                {loading ? 'Inspeccionando Mensaje...' : 'Ejecutar Diagnóstico de Amenaza'}
              </Button>
            </div>
          </Card>

          {/* Panel de Veredicto Forense */}
          <Card
            variant={result ? (simulatedIsSpam ? 'threat' : 'safe') : 'default'}
            className="lg:col-span-5 p-5 flex flex-col justify-between"
          >
            <div>
              <div className="flex items-center justify-between pb-3 border-b app-border mb-4">
                <span className="text-xs font-mono app-text-secondary font-bold">
                  VEREDICTO DE SEGURIDAD
                </span>
                <Badge variant={result ? (simulatedIsSpam ? 'danger' : 'safe') : 'neutral'}>
                  {result
                    ? simulatedIsSpam
                      ? feedbackStatus === 'corrected'
                        ? 'AMENAZA (CORREGIDO)'
                        : 'AMENAZA CONFIRMADA'
                      : feedbackStatus === 'corrected'
                      ? 'ORIGEN LEGÍTIMO (CORREGIDO)'
                      : 'ORIGEN LEGÍTIMO'
                    : 'A LA ESPERA'}
                </Badge>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="app-text-secondary">Índice de Probabilidad de Phishing:</span>
                    <span
                      className={`font-bold ${
                        result ? (simulatedIsSpam ? 'text-[#ef233c]' : 'text-[#8d99ae]') : 'app-text-primary'
                      }`}
                    >
                      {spamPercentage}%
                    </span>
                  </div>
                  <div className="w-full app-card-subtle border app-border h-3 overflow-hidden relative">
                    <div
                      className={`h-full ${simulatedIsSpam ? 'bg-[#ef233c]' : 'bg-[#4361ee]'}`}
                      style={{ width: `${spamPercentage}%` }}
                    />
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-yellow-400 z-10"
                      style={{ left: `${threshold * 100}%` }}
                      title={`Umbral de corte: ${(threshold * 100).toFixed(0)}%`}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] app-text-muted font-mono mt-0.5">
                    <span>0% (Inocuo)</span>
                    <span className="text-yellow-400">Corte: {(threshold * 100).toFixed(0)}%</span>
                    <span>100% (Crítico)</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-semibold app-text-primary block font-mono">
                    Indicadores Forenses Aislados:
                  </span>
                  <div className="flex flex-wrap gap-1.5 min-h-[32px] items-center">
                    {result && result.detected_tokens && result.detected_tokens.length > 0 ? (
                      result.detected_tokens.map((token, idx) => {
                        const isUrl = token === 'TOKEN_URL';
                        return (
                          <Badge
                            key={idx}
                            variant={isUrl ? 'danger' : 'neutral'}
                          >
                            {token}
                          </Badge>
                        );
                      })
                    ) : result ? (
                      <span className="text-xs app-text-muted font-mono flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5 text-[#8d99ae]" />
                        No se identificaron patrones de riesgo léxico.
                      </span>
                    ) : (
                      <span className="text-xs app-text-muted font-mono">
                        Ingrese un texto para obtener el reporte forense.
                      </span>
                    )}
                  </div>
                </div>

                {result && (
                  <div className="pt-2">
                    <div className="text-xs font-mono app-text-secondary flex justify-between">
                      <span>Nivel de Riesgo Evaluado:</span>
                      <span
                        className={`font-bold ${
                          result.risk_level === 'CRÍTICO'
                            ? 'text-[#ef233c]'
                            : result.risk_level === 'MEDIO'
                            ? 'text-yellow-400'
                            : 'text-green-400'
                        }`}
                      >
                        {result.risk_level}
                      </span>
                    </div>
                  </div>
                )}

                {/* Botones de Feedback Humano / Active Learning */}
                {result && (
                  <div className="pt-3 border-t app-border space-y-2">
                    <div className="flex items-center justify-between text-xs font-mono">
                      <span className="app-text-secondary flex items-center gap-1">
                        <CheckCircle2 className="w-3.5 h-3.5 text-[#4361ee]" />
                        Validación del Veredicto:
                      </span>
                      {feedbackStatus && (
                        <span
                          className={`text-[10px] font-bold font-mono ${
                            feedbackStatus === 'correct' ? 'text-green-400' : 'text-yellow-400'
                          }`}
                        >
                          {feedbackStatus === 'correct'
                            ? '✓ Veredicto Confirmado'
                            : '⚡ Corrección Registrada'}
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        type="button"
                        variant={feedbackStatus === 'correct' ? 'primary' : 'outline'}
                        size="sm"
                        onClick={() => handleFeedback('confirm')}
                        className="flex-1 flex items-center justify-center gap-1.5"
                      >
                        <ThumbsUp className="w-3.5 h-3.5" />
                        <span>Es Correcto</span>
                      </Button>
                      <Button
                        type="button"
                        variant={feedbackStatus === 'corrected' ? 'danger' : 'outline'}
                        size="sm"
                        onClick={() => handleFeedback('invert')}
                        className="flex-1 flex items-center justify-center gap-1.5"
                      >
                        <ThumbsDown className="w-3.5 h-3.5" />
                        <span>Corregir Veredicto</span>
                      </Button>
                    </div>
                    {feedbackStatus === 'corrected' && (
                      <p className="text-[10px] app-text-muted font-mono">
                        La muestra fue reetiquetada como {simulatedIsSpam ? 'amenaza' : 'legítimo'} para la próxima ronda de reentrenamiento continuo (Active Learning).
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>

            <div className="border-t app-border pt-3 mt-4 text-xs font-mono app-text-muted flex justify-between">
              <span className="flex items-center gap-1">
                <Shield className="w-3.5 h-3.5 text-[#4361ee]" />
                Motor: Pipeline Activo
              </span>
              <span>Latencia: {result ? `${result.latency_ms} ms` : '—'}</span>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
