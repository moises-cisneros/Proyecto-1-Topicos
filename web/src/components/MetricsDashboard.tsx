import React, { useEffect, useState } from 'react';
import { MetricsResponse, ModelBenchmarkItem, getMetrics } from '../services/api';
import { Award, BarChart3, CheckCircle2, RefreshCw, XCircle } from 'lucide-react';

export const MetricsDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedModelIdx, setSelectedModelIdx] = useState<number>(1); // Default to winner or LR

  const loadMetricsData = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getMetrics();
      setMetrics(data);
      // Auto select the winner model if present
      const winnerIdx = data.benchmark_summary.findIndex((m) =>
        m.model_name.toLowerCase().includes('logistic')
      );
      if (winnerIdx !== -1) {
        setSelectedModelIdx(winnerIdx);
      }
    } catch {
      setError('No se pudieron recuperar las métricas desde /metrics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMetricsData();
  }, []);

  if (loading) {
    return (
      <div className="app-card border rounded-xl p-8 text-center text-xs font-mono app-text-muted flex items-center justify-center gap-2">
        <RefreshCw className="w-4 h-4" />
        Cargando métricas y benchmarks de modelos...
      </div>
    );
  }

  if (error || !metrics) {
    return (
      <div className="bg-[#3a1017] border border-[#ef233c] text-[#ef233c] text-xs p-4 rounded-xl font-mono flex items-center justify-between">
        <span>{error || 'Error al cargar métricas'}</span>
        <button
          type="button"
          onClick={loadMetricsData}
          className="bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-3 py-1 rounded"
        >
          Reintentar
        </button>
      </div>
    );
  }

  const selectedModel: ModelBenchmarkItem =
    metrics.benchmark_summary[selectedModelIdx] || metrics.benchmark_summary[0];
  const { confusion_matrix } = selectedModel;

  return (
    <div className="space-y-6">
      <div className="border-b app-border pb-2 flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-semibold app-text-primary">
              Panel de Evaluación y Rendimiento ML
            </h2>
            <span className="bg-[#1c2e28] text-[#a8dadc] border border-[#8d99ae] text-xs font-mono px-2 py-0.5 rounded font-bold flex items-center gap-1">
              <Award className="w-3.5 h-3.5 text-yellow-400" />
              Ganador: {metrics.winner_model}
            </span>
          </div>
          <p className="text-xs app-text-secondary mt-1">
            Evaluación sobre conjunto holdout independiente (1.115 SMS) con 5-Fold Stratified Cross-Validation.
          </p>
        </div>

        {/* Selector de Modelo para Matriz */}
        <div className="flex flex-wrap items-center gap-2">
          {metrics.benchmark_summary.map((m, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => setSelectedModelIdx(idx)}
              className={`text-xs font-mono px-3 py-1.5 rounded border ${
                selectedModelIdx === idx
                  ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                  : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
              }`}
            >
              {m.model_name.replace(' (Challenger)', '').replace(' (Baseline)', '')}
            </button>
          ))}
        </div>
      </div>

      {/* Grid: Matriz de Confusión y Métricas Agregadas */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Matriz de Confusión 2x2 */}
        <div className="lg:col-span-6 app-card border rounded-xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b app-border pb-2">
            <h3 className="text-sm font-semibold app-text-primary font-mono flex items-center gap-2">
              <BarChart3 className="w-4 h-4 text-[#4361ee]" />
              Matriz de Confusión: {selectedModel.model_name}
            </h3>
            <span className="text-xs font-mono app-text-muted">Test N = 1,115</span>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2">
            {/* Verdaderos Negativos (TN) */}
            <div className="app-card-subtle border border-[#8d99ae] p-4 rounded-lg flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs font-mono text-[#a8dadc]">
                <span>Verdaderos Negativos (TN)</span>
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold font-mono text-[#edf2f4] my-2">
                {confusion_matrix.tn}
              </div>
              <div className="text-[11px] app-text-muted font-mono">
                Legítimos clasificados como Ham
              </div>
            </div>

            {/* Falsos Positivos (FP) - CRÍTICO */}
            <div className="bg-[#3a1017] border border-[#ef233c] p-4 rounded-lg flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs font-mono text-[#ef233c] font-bold">
                <span>Falsos Positivos (FP)</span>
                <XCircle className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold font-mono text-[#ef233c] my-2">
                {confusion_matrix.fp}
              </div>
              <div className="text-[11px] text-[#ef233c] font-mono">
                Tasa FP: {(selectedModel.rates.false_positive_rate * 100).toFixed(2)}%
              </div>
            </div>

            {/* Falsos Negativos (FN) */}
            <div className="app-card-subtle border border-[#8d99ae] p-4 rounded-lg flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs font-mono text-yellow-400">
                <span>Falsos Negativos (FN)</span>
                <AlertTriangleIcon className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold font-mono text-yellow-400 my-2">
                {confusion_matrix.fn}
              </div>
              <div className="text-[11px] app-text-muted font-mono">
                Tasa FN: {(selectedModel.rates.false_negative_rate * 100).toFixed(2)}%
              </div>
            </div>

            {/* Verdaderos Positivos (TP) */}
            <div className="app-card-subtle border border-[#4361ee] p-4 rounded-lg flex flex-col justify-between">
              <div className="flex items-center justify-between text-xs font-mono text-[#4361ee] font-bold">
                <span>Verdaderos Positivos (TP)</span>
                <CheckCircle2 className="w-4 h-4" />
              </div>
              <div className="text-2xl font-bold font-mono text-[#4361ee] my-2">
                {confusion_matrix.tp}
              </div>
              <div className="text-[11px] app-text-muted font-mono">
                Spam clasificado correctamente
              </div>
            </div>
          </div>
        </div>

        {/* Desglose de Métricas del Modelo Seleccionado */}
        <div className="lg:col-span-6 app-card border rounded-xl p-5 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between border-b app-border pb-2 mb-3">
              <h3 className="text-sm font-semibold app-text-primary font-mono">
                Métricas por Clase (Holdout 20%)
              </h3>
              <span className="text-xs font-mono text-[#4361ee] font-bold">
                F1-Macro: {(selectedModel.aggregate_metrics.f1_macro * 100).toFixed(2)}%
              </span>
            </div>

            <div className="space-y-3">
              {/* Ham */}
              <div className="app-card-subtle border app-border p-3 rounded-lg font-mono text-xs space-y-1">
                <div className="flex justify-between font-bold text-[#a8dadc]">
                  <span>Clase HAM (Legítimos - Support {selectedModel.class_metrics.ham.support})</span>
                  <span>F1: {(selectedModel.class_metrics.ham.f1_score * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between text-[11px] app-text-secondary">
                  <span>Precisión: {(selectedModel.class_metrics.ham.precision * 100).toFixed(2)}%</span>
                  <span>Recall: {(selectedModel.class_metrics.ham.recall * 100).toFixed(2)}%</span>
                </div>
              </div>

              {/* Spam */}
              <div className="app-card-subtle border app-border p-3 rounded-lg font-mono text-xs space-y-1">
                <div className="flex justify-between font-bold text-[#ef233c]">
                  <span>Clase SPAM (Phishing - Support {selectedModel.class_metrics.spam.support})</span>
                  <span>F1: {(selectedModel.class_metrics.spam.f1_score * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between text-[11px] app-text-secondary">
                  <span>Precisión: {(selectedModel.class_metrics.spam.precision * 100).toFixed(2)}%</span>
                  <span>Recall: {(selectedModel.class_metrics.spam.recall * 100).toFixed(2)}%</span>
                </div>
              </div>
            </div>
          </div>

          <div className="border-t app-border pt-3 mt-4 text-xs font-mono app-text-muted flex justify-between">
            <span>Exactitud (Accuracy): {(selectedModel.aggregate_metrics.accuracy * 100).toFixed(2)}%</span>
            <span>Tiempo Entrenamiento: {selectedModel.training_duration_seconds}s</span>
          </div>
        </div>
      </div>

      {/* Tabla Comparativa de Todos los Modelos Evaluados */}
      <div className="app-card border rounded-xl overflow-hidden">
        <div className="p-4 border-b app-border bg-[#232537]">
          <h3 className="text-sm font-semibold app-text-primary font-mono">
            Tabla Comparativa de Benchmarking (Línea Base vs Candidatos)
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs">
            <thead className="bg-[#2b2d42] border-b app-border text-[#edf2f4]">
              <tr>
                <th className="p-3">Modelo</th>
                <th className="p-3">Accuracy</th>
                <th className="p-3">F1 Spam</th>
                <th className="p-3">Recall Spam</th>
                <th className="p-3">Falsos Positivos</th>
                <th className="p-3">F1 Macro</th>
              </tr>
            </thead>
            <tbody className="divide-y app-border">
              {metrics.benchmark_summary.map((m, idx) => {
                const isSelected = selectedModelIdx === idx;
                return (
                  <tr
                    key={idx}
                    onClick={() => setSelectedModelIdx(idx)}
                    className={`cursor-pointer hover:bg-[#232537] ${
                      isSelected ? 'bg-[#232537] font-bold text-white' : 'app-text-secondary'
                    }`}
                  >
                    <td className="p-3 flex items-center gap-2">
                      {m.model_name.includes('Logistic') && (
                        <span className="w-2 h-2 rounded-full bg-[#4361ee]" />
                      )}
                      {m.model_name}
                    </td>
                    <td className="p-3">{(m.aggregate_metrics.accuracy * 100).toFixed(2)}%</td>
                    <td className="p-3 text-[#ef233c] font-bold">
                      {(m.class_metrics.spam.f1_score * 100).toFixed(2)}%
                    </td>
                    <td className="p-3">{(m.class_metrics.spam.recall * 100).toFixed(2)}%</td>
                    <td className="p-3">{m.confusion_matrix.fp}</td>
                    <td className="p-3 text-[#4361ee] font-bold">
                      {(m.aggregate_metrics.f1_macro * 100).toFixed(2)}%
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// Ícono auxiliar
function AlertTriangleIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      {...props}
    >
      <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z" />
      <line x1="12" y1="9" x2="12" y2="13" />
      <line x1="12" y1="17" x2="12.01" y2="17" />
    </svg>
  );
}
