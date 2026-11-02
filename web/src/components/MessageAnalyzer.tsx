import React, { useState } from 'react';
import { PredictionResponse, predictMessage } from '../services/api';
import { BatchAnalyzer } from './BatchAnalyzer';
import {
  AlertTriangle,
  CheckCircle,
  FileSpreadsheet,
  MessageSquare,
  ShieldAlert,
  Sliders,
  Sparkles,
  Trash2,
} from 'lucide-react';

interface MessageAnalyzerProps {
  onAnalyzeSuccess?: (text: string, result: PredictionResponse) => void;
  onInspectBatchMessage?: (text: string) => void;
}

const SAMPLE_HAM =
  'Hola Carlos, te paso el resumen de la reunión de hoy. Mañana seguimos con el informe.';
const SAMPLE_SPAM =
  'ALERTA BANCO: Transferencia no autorizada de $4,500 en curso. Ingrese a https://bit.ly/banco o llame al 800-449922 urgente.';

export const MessageAnalyzer: React.FC<MessageAnalyzerProps> = ({
  onAnalyzeSuccess,
  onInspectBatchMessage,
}) => {
  const [analysisMode, setAnalysisMode] = useState<'single' | 'batch'>('single');
  const [text, setText] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [threshold, setThreshold] = useState<number>(0.50);

  const charCount = text.length;
  const wordCount = text.trim() === '' ? 0 : text.trim().split(/\s+/).length;
  const smsSegments = Math.ceil(charCount / 160) || 1;

  const handleClear = () => {
    setText('');
    setError(null);
    setResult(null);
  };

  const handleLoadSample = (type: 'ham' | 'spam') => {
    const sample = type === 'ham' ? SAMPLE_HAM : SAMPLE_SPAM;
    setText(sample);
    setError(null);
  };

  const handleAnalyze = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const cleanText = text.trim();
    if (!cleanText) {
      setError('El texto no puede estar vacío ni contener sólo espacios.');
      setResult(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await predictMessage(cleanText);
      setResult(response);
      if (onAnalyzeSuccess) {
        onAnalyzeSuccess(cleanText, response);
      }
    } catch (err: unknown) {
      if (typeof err === 'object' && err !== null && 'response' in err) {
        const axErr = err as { response?: { data?: { detail?: string | { msg?: string }[] } } };
        const detail = axErr.response?.data?.detail;
        if (typeof detail === 'string') {
          setError(detail);
        } else if (Array.isArray(detail) && detail.length > 0 && detail[0].msg) {
          setError(detail[0].msg);
        } else {
          setError('Error de validación al procesar el mensaje (HTTP 422).');
        }
      } else {
        setError('No se pudo conectar con el microservicio API (puerto 8090).');
      }
    } finally {
      setLoading(false);
    }
  };

  // Diagnóstico reactivo basado en el umbral calibrado en vivo
  const rawSpamProb = result ? result.spam_probability : 0.0;
  const simulatedIsSpam = result ? rawSpamProb >= threshold : false;
  const spamPercentage = (rawSpamProb * 100).toFixed(1);

  return (
    <div className="space-y-6">
      {/* Selector de Modo de Escaneo */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b app-border pb-3">
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setAnalysisMode('single')}
            className={`px-3.5 py-1.5 text-xs font-mono rounded-md flex items-center gap-2 border ${
              analysisMode === 'single'
                ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            Escáner Forense Individual
          </button>
          <button
            type="button"
            onClick={() => setAnalysisMode('batch')}
            className={`px-3.5 py-1.5 text-xs font-mono rounded-md flex items-center gap-2 border ${
              analysisMode === 'batch'
                ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
            }`}
          >
            <FileSpreadsheet className="w-3.5 h-3.5" />
            Ingesta Masiva de Datasets (.CSV)
          </button>
        </div>

        {analysisMode === 'single' && (
          <div className="flex items-center gap-2 text-xs font-mono app-text-secondary bg-[#232537] px-3 py-1.5 rounded-lg border app-border">
            <Sliders className="w-3.5 h-3.5 text-[#4361ee]" />
            <span>Umbral de Alerta:</span>
            <input
              type="range"
              min="0.20"
              max="0.80"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="w-24 accent-[#4361ee] cursor-pointer"
            />
            <span className="font-bold text-[#edf2f4]">{(threshold * 100).toFixed(0)}%</span>
            <span className="text-[10px] text-[#8d99ae]">
              ({threshold <= 0.35 ? 'Agresivo' : threshold >= 0.65 ? 'Conservador' : 'Balanceado'})
            </span>
          </div>
        )}
      </div>

      {/* Renderizado Condicional del Modo */}
      {analysisMode === 'batch' ? (
        <BatchAnalyzer onInspectMessage={onInspectBatchMessage} />
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Panel Izquierdo: Entrada de Texto */}
          <div className="lg:col-span-7 app-card border rounded-xl p-5 space-y-4">
            <div className="flex flex-wrap items-center justify-between gap-2">
              <label htmlFor="smsInput" className="text-sm font-semibold app-text-primary">
                Texto del SMS en Español:
              </label>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleLoadSample('ham')}
                  className="text-xs bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-2.5 py-1 rounded hover:bg-[#393c59]"
                >
                  Cargar Legítimo
                </button>
                <button
                  type="button"
                  onClick={() => handleLoadSample('spam')}
                  className="text-xs bg-[#ef233c] text-[#edf2f4] px-2.5 py-1 rounded hover:bg-[#d61e33]"
                >
                  Cargar Phishing
                </button>
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
              className="w-full app-card-subtle border app-border-solid rounded-lg p-3 app-text-primary font-sans text-sm focus:outline-none focus:ring-2 focus:ring-[#4361ee]"
              placeholder="Pegue aquí el SMS para clasificar con el pipeline NLP..."
            />

            <div className="flex items-center justify-between text-xs app-text-secondary font-mono border-t app-border pt-3">
              <span>
                Caracteres: {charCount} / 160 ({smsSegments} SMS) | Palabras: {wordCount}
              </span>
              <button
                type="button"
                onClick={handleClear}
                className="app-text-muted hover:app-text-primary flex items-center gap-1"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Limpiar
              </button>
            </div>

            {error && (
              <div className="bg-[#3a1017] border border-[#ef233c] text-[#ef233c] text-xs p-3 rounded font-mono flex items-center gap-2">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <div className="pt-2">
              <button
                type="button"
                disabled={loading}
                onClick={() => handleAnalyze()}
                className="w-full btn-cta font-medium py-2.5 rounded-md text-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Sparkles className="w-4 h-4" />
                {loading ? 'Analizando Mensaje...' : 'Analizar Mensaje con Pipeline NLP'}
              </button>
            </div>
          </div>

          {/* Panel Derecho: Diagnóstico Forense en Vivo */}
          <div
            className={`lg:col-span-5 app-card border-2 rounded-xl p-5 flex flex-col justify-between ${
              result
                ? simulatedIsSpam
                  ? 'border-[#ef233c]'
                  : 'border-[#8d99ae]'
                : 'border-transparent'
            }`}
          >
            <div>
              <div className="flex items-center justify-between pb-3 border-b app-border mb-4">
                <span className="text-xs font-mono app-text-secondary font-bold">
                  DIAGNÓSTICO EN VIVO
                </span>
                <span
                  className={`font-mono text-xs px-2.5 py-0.5 rounded font-bold ${
                    result
                      ? simulatedIsSpam
                        ? 'badge-phishing'
                        : 'badge-legit'
                      : 'bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae]'
                  }`}
                >
                  {result
                    ? simulatedIsSpam
                      ? 'AMENAZA DE PHISHING'
                      : 'MENSAJE LEGÍTIMO'
                    : 'ESPERANDO ENTRADA'}
                </span>
              </div>

              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-xs font-mono mb-1">
                    <span className="app-text-secondary">Probabilidad de Amenaza:</span>
                    <span
                      className={`font-bold ${
                        result ? (simulatedIsSpam ? 'text-[#ef233c]' : 'text-[#8d99ae]') : 'app-text-primary'
                      }`}
                    >
                      {spamPercentage}%
                    </span>
                  </div>
                  <div className="w-full app-card-subtle border app-border h-3 rounded-none overflow-hidden relative">
                    <div
                      className={`h-full ${simulatedIsSpam ? 'bg-[#ef233c]' : 'bg-[#4361ee]'}`}
                      style={{ width: `${spamPercentage}%` }}
                    />
                    {/* Marcador del Umbral en la barra */}
                    <div
                      className="absolute top-0 bottom-0 w-0.5 bg-yellow-400 z-10"
                      style={{ left: `${threshold * 100}%` }}
                      title={`Umbral de decisión: ${(threshold * 100).toFixed(0)}%`}
                    />
                  </div>
                  <div className="flex justify-between text-[10px] text-[#8d99ae] font-mono mt-0.5">
                    <span>0%</span>
                    <span className="text-yellow-400">Umbral: {(threshold * 100).toFixed(0)}%</span>
                    <span>100%</span>
                  </div>
                </div>

                <div className="space-y-2">
                  <span className="text-xs font-medium app-text-primary block">
                    Entidades y Vectores Detectados:
                  </span>
                  <div className="flex flex-wrap gap-1.5 min-h-[32px] items-center">
                    {result && result.detected_tokens && result.detected_tokens.length > 0 ? (
                      result.detected_tokens.map((token, idx) => {
                        let badgeClass = 'bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae]';
                        if (token === 'TOKEN_URL') {
                          badgeClass = 'bg-[#ef233c] text-[#edf2f4]';
                        } else if (token === 'TOKEN_TEL') {
                          badgeClass = 'bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae]';
                        } else if (token.includes('URG')) {
                          badgeClass = 'bg-[#4361ee] text-white font-bold';
                        }
                        return (
                          <span
                            key={idx}
                            className={`font-mono text-xs px-2 py-0.5 rounded ${badgeClass}`}
                          >
                            {token}
                          </span>
                        );
                      })
                    ) : result ? (
                      <span className="text-xs app-text-muted font-mono flex items-center gap-1">
                        <CheckCircle className="w-3.5 h-3.5 text-[#8d99ae]" />
                        Sin vectores maliciosos detectados.
                      </span>
                    ) : (
                      <span className="text-xs app-text-muted font-mono">
                        Ingrese un mensaje para ejecutar el análisis forense.
                      </span>
                    )}
                  </div>
                </div>

                {result && (
                  <div className="pt-2">
                    <div className="text-xs font-mono app-text-secondary flex justify-between">
                      <span>Riesgo Semántico:</span>
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
              </div>
            </div>

            <div className="border-t app-border pt-3 mt-4 text-xs font-mono app-text-muted flex justify-between">
              <span className="flex items-center gap-1">
                <ShieldAlert className="w-3.5 h-3.5 text-[#4361ee]" />
                Modelo: Pipeline en Producción
              </span>
              <span>Latencia: {result ? `${result.latency_ms} ms` : '—'}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
