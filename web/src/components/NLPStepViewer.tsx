import React, { useEffect, useState } from 'react';
import { NLPDebugResponse, debugNLP } from '../services/api';
import { ArrowRight, Code, FileText, Layers, RefreshCw } from 'lucide-react';

interface NLPStepViewerProps {
  currentText?: string;
}

const DEFAULT_SAMPLE =
  'ALERTA BANCO: Transferencia no autorizada de $4,500 en curso. Ingrese a https://bit.ly/banco o llame al 800-449922 urgente.';

export const NLPStepViewer: React.FC<NLPStepViewerProps> = ({ currentText }) => {
  const [activeStep, setActiveStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [debugData, setDebugData] = useState<NLPDebugResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchDebugInfo = async (textToDebug: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await debugNLP(textToDebug);
      setDebugData(data);
    } catch {
      setError('No se pudo obtener la traza de depuración desde el endpoint /nlp/debug.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const text = currentText?.trim() || DEFAULT_SAMPLE;
    fetchDebugInfo(text);
  }, [currentText]);

  // Contenido formativo por paso según datos de la API o valores por defecto
  const renderStepContent = () => {
    if (loading) {
      return (
        <div className="p-6 text-center text-xs font-mono app-text-muted flex items-center justify-center gap-2">
          <RefreshCw className="w-4 h-4" />
          Procesando trazabilidad del pipeline NLP...
        </div>
      );
    }

    if (error && !debugData) {
      return (
        <div className="p-6 text-xs font-mono text-[#ef233c] bg-[#3a1017] border border-[#ef233c] rounded-lg">
          {error}
        </div>
      );
    }

    switch (activeStep) {
      case 1:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <FileText className="w-4 h-4 text-[#4361ee]" />
              Paso 01: Texto Original del Usuario
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              Cadena de texto recibida sin ningún tipo de modificación o filtro.
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm app-text-secondary whitespace-pre-line">
              {debugData?.original || currentText || DEFAULT_SAMPLE}
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#4361ee]" />
              Paso 02: Enmascaramiento Regex y Normalización
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              Normalización a minúsculas, eliminación de acentos diacríticos y sustitución regex de
              patrones críticos: URLs → <code className="text-[#ef233c]">TOKEN_URL</code>, Teléfonos →{' '}
              <code className="text-[#4361ee]">TOKEN_TEL</code> y Cantidades →{' '}
              <code className="text-[#edf2f4]">TOKEN_NUM</code>.
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm app-text-secondary whitespace-pre-line">
              {debugData?.normalized || 'Sin datos de normalización.'}
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <Code className="w-4 h-4 text-[#4361ee]" />
              Paso 03: Tokenización Boundary-Safe
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              División en unidades léxicas respetando límites de palabras y preservando íntegros los
              tokens sintéticos generados en la fase previa.
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm text-[#edf2f4] flex flex-wrap gap-1.5">
              {debugData?.tokens && debugData.tokens.length > 0 ? (
                debugData.tokens.map((tok, i) => (
                  <span
                    key={i}
                    className="bg-[#2b2d42] border border-[#8d99ae] px-2 py-0.5 rounded text-xs"
                  >
                    {tok}
                  </span>
                ))
              ) : (
                <span className="app-text-muted">No se extrajeron tokens.</span>
              )}
            </div>
          </div>
        );

      case 4:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#4361ee]" />
              Paso 04: Stop Words Filtradas (Whitelist Preservada)
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              Eliminación de palabras vacías no informativas del español (artículos, preposiciones),
              manteniendo la whitelist estricta para negaciones (<code className="text-white">no, sin</code>)
              y vectores de urgencia (<code className="text-white">urgente, bloqueo, ya</code>).
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm text-[#edf2f4] flex flex-wrap gap-1.5">
              {debugData?.no_stopwords && debugData.no_stopwords.length > 0 ? (
                debugData.no_stopwords.map((tok, i) => (
                  <span
                    key={i}
                    className="bg-[#232537] border border-[#4361ee] text-[#edf2f4] px-2 py-0.5 rounded text-xs"
                  >
                    {tok}
                  </span>
                ))
              ) : (
                <span className="app-text-muted">No quedaron tokens tras filtrado.</span>
              )}
            </div>
          </div>
        );

      case 5:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <Layers className="w-4 h-4 text-[#4361ee]" />
              Paso 05: Reducción Morfológica (Snowball Stemming)
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              Extracción de raíces léxicas en español para compactar el vocabulario y potenciar la
              frecuencia de términos raíz sin fragmentar los tokens sintéticos.
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm text-[#edf2f4] flex flex-wrap gap-1.5">
              {debugData?.stemmed_or_lemmatized && debugData.stemmed_or_lemmatized.length > 0 ? (
                debugData.stemmed_or_lemmatized.map((stem, i) => (
                  <span
                    key={i}
                    className="bg-[#1c2e28] border border-[#8d99ae] text-[#a8dadc] px-2 py-0.5 rounded text-xs"
                  >
                    {stem}
                  </span>
                ))
              ) : (
                <span className="app-text-muted">Sin raíces generadas.</span>
              )}
            </div>
          </div>
        );

      case 6:
        return (
          <div>
            <h4 className="text-sm font-semibold app-text-primary mb-2 font-mono flex items-center gap-2">
              <ArrowRight className="w-4 h-4 text-[#4361ee]" />
              Paso 06: Vector TF-IDF Sublineal (Top Términos Ponderados)
            </h4>
            <p className="text-xs app-text-secondary mb-3">
              Ponderación numérica calculada por el vectorizador TF-IDF con sublinear_tf=True
              para amortiguar repeticiones artificiales.
            </p>
            <div className="app-card-subtle border app-border p-4 rounded-lg font-mono text-sm space-y-2">
              {debugData?.tfidf_top_features && debugData.tfidf_top_features.length > 0 ? (
                debugData.tfidf_top_features.map((item, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between border-b app-border pb-1.5 last:border-b-0"
                  >
                    <span className="text-xs font-bold text-[#edf2f4]">
                      {idx + 1}. {item.feature}
                    </span>
                    <span className="text-xs font-mono text-[#4361ee] bg-[#2b2d42] px-2 py-0.5 rounded border border-[#8d99ae]">
                      Peso: {item.weight.toFixed(4)}
                    </span>
                  </div>
                ))
              ) : (
                <span className="text-xs app-text-muted">
                  No se identificaron características con peso TF-IDF en el vocabulario entrenado.
                </span>
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const steps = [
    { id: 1, label: '01. Texto Crudo' },
    { id: 2, label: '02. Regex Masking' },
    { id: 3, label: '03. Tokens' },
    { id: 4, label: '04. Stopwords' },
    { id: 5, label: '05. Stemming' },
    { id: 6, label: '06. TF-IDF Top 5' },
  ];

  return (
    <div className="space-y-4">
      <div className="border-b app-border pb-2 flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold app-text-primary">
            Visor Interactivo del Pipeline NLP (6 Etapas)
          </h2>
          <p className="text-xs app-text-secondary">
            Inspección paso a paso de las transformaciones intermedias generadas por el pipeline serializado.
          </p>
        </div>
        <button
          type="button"
          onClick={() => fetchDebugInfo(currentText?.trim() || DEFAULT_SAMPLE)}
          className="text-xs font-mono bg-[#2b2d42] text-[#edf2f4] border border-[#8d99ae] px-3 py-1.5 rounded hover:bg-[#393c59] flex items-center gap-1.5"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Actualizar Traza
        </button>
      </div>

      <div className="app-card border rounded-xl overflow-hidden">
        {/* Pestañas de Navegación de Etapas */}
        <div className="flex flex-wrap border-b app-border app-card-subtle font-mono text-xs">
          {steps.map((st) => (
            <button
              key={st.id}
              type="button"
              onClick={() => setActiveStep(st.id)}
              className={`px-4 py-2.5 border-r app-border text-xs ${
                activeStep === st.id
                  ? 'app-card text-[#4361ee] font-bold border-b-2 border-b-[#4361ee]'
                  : 'app-text-secondary hover:app-text-primary'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>

        {/* Panel de Contenido de la Etapa */}
        <div className="p-6">{renderStepContent()}</div>
      </div>
    </div>
  );
};
