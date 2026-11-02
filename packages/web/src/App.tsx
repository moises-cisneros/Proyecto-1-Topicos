import React, { useEffect, useState } from 'react';
import { MessageAnalyzer } from './components/MessageAnalyzer';
import { NLPStepViewer } from './components/NLPStepViewer';
import { MetricsDashboard } from './components/MetricsDashboard';
import { HistoryAuditTable } from './components/HistoryAuditTable';
import {
  Activity,
  BarChart2,
  Clock,
  Moon,
  Shield,
  Sun,
} from 'lucide-react';
import { PredictionResponse } from './services/api';
import { Button } from './components/ui/Button';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'metrics' | 'history'>(() => {
    const saved = localStorage.getItem('sms_sentinel_active_tab');
    if (saved === 'analyzer' || saved === 'metrics' || saved === 'history') {
      return saved;
    }
    return 'analyzer';
  });

  const [isLightMode, setIsLightMode] = useState<boolean>(() => {
    return localStorage.getItem('sms_sentinel_theme') === 'light';
  });

  const [analyzedText, setAnalyzedText] = useState<string>(() => {
    return localStorage.getItem('sms_sentinel_analyzed_text') || '';
  });

  const [selectedHistoryText, setSelectedHistoryText] = useState<string>('');

  useEffect(() => {
    localStorage.setItem('sms_sentinel_active_tab', activeTab);
  }, [activeTab]);

  useEffect(() => {
    if (isLightMode) {
      document.documentElement.classList.add('light');
      document.body.classList.add('theme-light');
      localStorage.setItem('sms_sentinel_theme', 'light');
    } else {
      document.documentElement.classList.remove('light');
      document.body.classList.remove('theme-light');
      localStorage.setItem('sms_sentinel_theme', 'dark');
    }
  }, [isLightMode]);

  useEffect(() => {
    if (analyzedText) {
      localStorage.setItem('sms_sentinel_analyzed_text', analyzedText);
    } else {
      localStorage.removeItem('sms_sentinel_analyzed_text');
    }
  }, [analyzedText]);

  const toggleTheme = () => {
    setIsLightMode((prev) => !prev);
  };

  const handleMessageAnalyzed = (text: string, _res: PredictionResponse) => {
    setAnalyzedText(text);
  };

  const handleSelectFromHistory = (text: string) => {
    setSelectedHistoryText(text);
    setAnalyzedText(text);
    setActiveTab('analyzer');
  };

  const handleInspectBatchMessage = (text: string) => {
    setSelectedHistoryText(text);
    setAnalyzedText(text);
  };

  return (
    <div className="app-canvas min-h-screen p-6 lg:p-10 flex flex-col justify-between">
      <div className="max-w-7xl mx-auto w-full space-y-6">
        {/* Encabezado y Telemetría */}
        <header className="border-b app-border pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="inline-block w-4 h-4 bg-[#4361ee] rounded-sm" />
              <h1 className="text-2xl font-bold tracking-tight app-text-primary flex items-center gap-2">
                <Shield className="w-6 h-6 text-[#4361ee]" />
                SMS Sentinel — Security Operations & Threat Gateway
              </h1>
            </div>
            <p className="text-xs app-text-secondary mt-1">
              Plataforma de ciberseguridad para detección temprana de Phishing, Smishing y estafas bancarias en mensajería en español.
            </p>
          </div>

          {/* Controles de Estado y Tema */}
          <div className="flex items-center">
            <Button
              variant="secondary"
              size="sm"
              onClick={toggleTheme}
              icon={isLightMode ? <Moon className="w-4 h-4" /> : <Sun className="w-4 h-4" />}
              aria-label="Alternar tema visual"
            />
          </div>
        </header>

        {/* Barra de Navegación */}
        <nav className="flex flex-wrap gap-2 border-b app-border pb-3">
          <Button
            variant={activeTab === 'analyzer' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setActiveTab('analyzer')}
            icon={<Activity className="w-4 h-4" />}
          >
            Escáner de Amenazas
          </Button>

          <Button
            variant={activeTab === 'metrics' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setActiveTab('metrics')}
            icon={<BarChart2 className="w-4 h-4" />}
          >
            Métricas del Modelo
          </Button>

          <Button
            variant={activeTab === 'history' ? 'primary' : 'secondary'}
            size="sm"
            onClick={() => setActiveTab('history')}
            icon={<Clock className="w-4 h-4" />}
          >
            Registro de Incidentes
          </Button>
        </nav>

        {/* Contenido de la Vista - Mantenido montado para preservar estado entre pestañas */}
        <main className="space-y-8">
          <div className={activeTab === 'analyzer' ? 'space-y-8' : 'hidden'}>
            <section>
              <div className="border-b app-border pb-2 mb-4">
                <h2 className="text-xl font-semibold app-text-primary">
                  Pasarela de Detección de Phishing y Spam
                </h2>
                <p className="text-xs app-text-secondary">
                  Inferencia individual y procesamiento masivo con calibración de umbrales y auditoría inmutable.
                </p>
              </div>
              <MessageAnalyzer
                externalText={selectedHistoryText}
                onAnalyzeSuccess={handleMessageAnalyzed}
                onInspectBatchMessage={handleInspectBatchMessage}
              />
            </section>

            <section>
              <NLPStepViewer currentText={analyzedText} />
            </section>
          </div>

          <div className={activeTab === 'metrics' ? 'block' : 'hidden'}>
            <MetricsDashboard />
          </div>

          <div className={activeTab === 'history' ? 'block' : 'hidden'}>
            <HistoryAuditTable onSelectMessage={handleSelectFromHistory} />
          </div>
        </main>
      </div>

      {/* Pie de Página */}
      <footer className="max-w-7xl mx-auto w-full mt-12 pt-6 border-t app-border text-xs app-text-muted flex flex-col sm:flex-row items-center justify-between gap-2 font-mono">
        <span>
          SMS Sentinel — Plataforma de Detección e Inteligencia de Amenazas
        </span>
        <div className="flex items-center gap-3">
          <span className="app-text-secondary">v1.0.0</span>
        </div>
      </footer>
    </div>
  );
};
export default App;
