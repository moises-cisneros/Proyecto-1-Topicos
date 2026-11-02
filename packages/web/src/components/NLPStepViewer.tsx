import React, { useEffect, useState } from 'react';
import { NLPDebugResponse, debugNLP } from '../services/api';
import { Shield, Hash, Search, Zap, BarChart2, AlertCircle } from 'lucide-react';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';
import sampleData from '@resources/example/samples.json';

interface NLPStepViewerProps {
  currentText?: string;
}

const DEFAULT_SAMPLE =
  sampleData.default_forensic_sample ||
  (sampleData.samples && sampleData.samples[0]?.text) ||
  '';

export const NLPStepViewer: React.FC<NLPStepViewerProps> = ({ currentText }) => {
  const [activeStep, setActiveStep] = useState<number>(() => {
    const saved = localStorage.getItem('sms_sentinel_nlp_active_step');
    const parsed = saved ? parseInt(saved, 10) : 1;
    return parsed >= 1 && parsed <= 5 ? parsed : 1;
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [debugData, setDebugData] = useState<NLPDebugResponse | null>(() => {
    try {
      const saved = localStorage.getItem('sms_sentinel_nlp_debug_data');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem('sms_sentinel_nlp_active_step', activeStep.toString());
  }, [activeStep]);

  useEffect(() => {
    if (debugData) {
      try {
        localStorage.setItem('sms_sentinel_nlp_debug_data', JSON.stringify(debugData));
      } catch {
        // Fallback for localStorage limits
      }
    } else {
      localStorage.removeItem('sms_sentinel_nlp_debug_data');
    }
  }, [debugData]);

  const fetchDebugInfo = async (textToDebug: string) => {
    setLoading(true);
    setError(null);
    try {
      const data = await debugNLP(textToDebug);
      setDebugData(data);
    } catch {
      setError('No fue posible obtener la traza forense del mensaje analizado.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (currentText && currentText.trim().length > 0) {
      fetchDebugInfo(currentText.trim());
    }
  }, [currentText]);

  const renderStepContent = () => {
    if (!currentText?.trim() && !debugData && !loading) {
      return (
        <Card variant="subtle" className="p-8 text-center text-xs font-mono app-text-muted">
          <Shield className="w-8 h-8 text-[#4361ee] mx-auto mb-2 opacity-80" />
          <p className="font-semibold text-sm app-text-primary mb-1">
            Inspector Forense de Señales Lingüísticas
          </p>
          <p className="max-w-md mx-auto mb-4">
            Analice un mensaje en el escáner superior para examinar el vector de ataque, enmascaramiento de entidades y ponderaciones léxicas en tiempo real.
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchDebugInfo(DEFAULT_SAMPLE)}
          >
            Cargar Muestra Forense
          </Button>
        </Card>
      );
    }

    if (loading) {
      return (
        <div className="p-6 text-center text-xs font-mono app-text-muted">
          Extrayendo indicadores forenses y pesos del modelo...
        </div>
      );
    }

    if (error) {
      return (
        <Card variant="subtle" className="p-4 flex items-center gap-2 text-xs font-mono text-[#ef233c]">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{error}</span>
        </Card>
      );
    }

    if (!debugData) return null;

    switch (activeStep) {
      case 1:
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="app-text-secondary font-semibold">
                Normalización y Enmascaramiento de Vectores
              </span>
              <Badge variant="neutral">Normalizado</Badge>
            </div>
            <p className="app-text-muted text-xs leading-relaxed">
              Las entidades de ataque (URLs, números telefónicos de contacto e importes) se reemplazan por tokens sintéticos para preservar el patrón semántico sin sobredimensionar el vocabulario.
            </p>
            <div className="p-3 rounded app-card-subtle border app-border text-xs leading-relaxed app-text-primary break-all">
              {debugData.normalized}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="app-text-secondary font-semibold">
                Segmentación Léxica Boundary-Safe
              </span>
              <Badge variant="neutral">{debugData.tokens.length} Tokens</Badge>
            </div>
            <p className="app-text-muted text-xs leading-relaxed">
              Segmentación con delimitación estricta de palabras que evita fracturas en tokens sintéticos protegidos.
            </p>
            <div className="flex flex-wrap gap-1.5 p-3 rounded app-card-subtle border app-border max-h-48 overflow-y-auto">
              {debugData.tokens.map((token, i) => {
                const isSynthetic = token.startsWith('TOKEN_');
                return (
                  <span
                    key={i}
                    className={`px-2 py-0.5 rounded text-xs border ${
                      isSynthetic
                        ? 'badge-phishing font-bold'
                        : 'app-card app-text-primary app-border'
                    }`}
                  >
                    {token}
                  </span>
                );
              })}
            </div>
          </div>
        );

      case 3:
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="app-text-secondary font-semibold">
                Léxico Depurado con Whitelist de Urgencia
              </span>
              <Badge variant="neutral">{debugData.no_stopwords.length} Términos</Badge>
            </div>
            <p className="app-text-muted text-xs leading-relaxed">
              Depuración de conectores vacíos en español, preservando explícitamente negaciones y disparadores léxicos de urgencia bancaria.
            </p>
            <div className="flex flex-wrap gap-1.5 p-3 rounded app-card-subtle border app-border max-h-48 overflow-y-auto">
              {debugData.no_stopwords.map((word, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-xs app-card app-text-primary border app-border"
                >
                  {word}
                </span>
              ))}
            </div>
          </div>
        );

      case 4:
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="app-text-secondary font-semibold">
                Raíces Léxicas Procesadas
              </span>
              <Badge variant="neutral">Lematización / Stemming</Badge>
            </div>
            <p className="app-text-muted text-xs leading-relaxed">
              Reducción morfológica determinista mediante Snowball Stemmer para consolidar variantes morfológicas y sufijos en raíces unificadas.
            </p>
            <div className="flex flex-wrap gap-1.5 p-3 rounded app-card-subtle border app-border max-h-48 overflow-y-auto">
              {debugData.stemmed_or_lemmatized.map((stem, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 rounded text-xs app-card text-[#a8dadc] border app-border font-bold"
                >
                  {stem}
                </span>
              ))}
            </div>
          </div>
        );

      case 5:
        return (
          <div className="space-y-3 font-mono text-xs">
            <div className="flex items-center justify-between">
              <span className="app-text-secondary font-semibold">
                Ponderación TF-IDF y Factores de Relevancia
              </span>
              <Badge variant="neutral">Top Coeficientes</Badge>
            </div>
            <p className="app-text-muted text-xs leading-relaxed">
              Términos con mayor peso estadístico TF-IDF sublineal que definen el sesgo del clasificador hacia amenaza o legitimidad.
            </p>
            <div className="space-y-2 p-3 rounded app-card-subtle border app-border">
              {debugData.tfidf_top_features.length === 0 ? (
                <p className="app-text-muted italic">No se registraron pesos significativos para este patrón.</p>
              ) : (
                debugData.tfidf_top_features.map((feat, i) => {
                  const pct = Math.min(100, Math.round(feat.weight * 100));
                  return (
                    <div key={i} className="flex items-center gap-3">
                      <span className="w-24 text-right app-text-primary font-bold truncate">
                        {feat.feature}
                      </span>
                      <div className="flex-1 bg-[#1e2030] border app-border h-3.5 rounded overflow-hidden">
                        <div
                          className="bg-[#4361ee] h-full"
                          style={{ width: `${pct}%` }}
                        />
                      </div>
                      <span className="w-14 text-right app-text-secondary font-mono">
                        {feat.weight.toFixed(4)}
                      </span>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  const tabs = [
    { id: 1, label: '01. Normalización', icon: Shield },
    { id: 2, label: '02. Tokens', icon: Hash },
    { id: 3, label: '03. Léxico Activo', icon: Search },
    { id: 4, label: '04. Morfología', icon: Zap },
    { id: 5, label: '05. Pesos TF-IDF', icon: BarChart2 },
  ];

  return (
    <Card className="p-5 font-mono">
      <div className="flex items-center justify-between border-b app-border pb-3 mb-4">
        <div>
          <h3 className="font-bold text-sm app-text-primary flex items-center gap-2">
            <Shield className="w-4 h-4 text-[#4361ee]" />
            Inspección Forense de Señales Lingüísticas
          </h3>
          <p className="text-xs app-text-muted mt-0.5">
            Trazabilidad del pipeline: enmascaramiento, tokens boundary-safe y coeficientes TF-IDF
          </p>
        </div>
        {debugData && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => currentText && fetchDebugInfo(currentText)}
          >
            Actualizar
          </Button>
        )}
      </div>

      {/* Selector de Vistas Forenses */}
      <div className="flex flex-wrap gap-2 mb-4 border-b app-border pb-3">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeStep === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveStep(tab.id)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-mono font-medium border cursor-pointer ${
                isActive
                  ? 'btn-cta'
                  : 'app-card-subtle app-text-secondary app-border hover:app-text-primary hover:border-[#8d99ae]'
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Contenido del Inspector */}
      {renderStepContent()}
    </Card>
  );
};
