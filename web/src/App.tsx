import React, { useEffect, useState } from 'react';
import { MessageAnalyzer } from './components/MessageAnalyzer';
import { NLPStepViewer } from './components/NLPStepViewer';
import { MetricsDashboard } from './components/MetricsDashboard';
import { HistoryAuditTable } from './components/HistoryAuditTable';
import { Activity, BarChart2, Database, Moon, Shield, Sun } from 'lucide-react';
import { PredictionResponse, checkHealth } from './services/api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analyzer' | 'metrics' | 'history'>('analyzer');
  const [isLightMode, setIsLightMode] = useState<boolean>(false);
  const [analyzedText, setAnalyzedText] = useState<string>('');
  const [backendStatus, setBackendStatus] = useState<string>('Verificando...');

  useEffect(() => {
    // Verificar salud inicial del backend
    checkHealth()
      .then((res) => setBackendStatus(`${res.status} (v${res.version})`))
      .catch(() => setBackendStatus('Desconectado'));
  }, []);

  const toggleTheme = () => {
    setIsLightMode(!isLightMode);
    if (!isLightMode) {
      document.documentElement.classList.add('light');
      document.body.classList.add('theme-light');
    } else {
      document.documentElement.classList.remove('light');
      document.body.classList.remove('theme-light');
    }
  };

  const handleMessageAnalyzed = (text: string, _res: PredictionResponse) => {
    setAnalyzedText(text);
  };

  const handleSelectFromHistory = (text: string) => {
    setAnalyzedText(text);
    setActiveTab('analyzer');
  };

  return (
    <div className="app-canvas min-h-screen p-6 lg:p-10 flex flex-col justify-between">
      <div className="max-w-7xl mx-auto w-full space-y-8">
        {/* Encabezado Principal */}
        <header className="border-b app-border pb-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-3">
              <span className="inline-block w-4 h-4 bg-[#4361ee]" />
              <h1 className="text-2xl font-bold tracking-tight app-text-primary flex items-center gap-2">
                <Shield className="w-6 h-6 text-[#4361ee]" />
                SMS Sentinel — Detección de Phishing y Spam
              </h1>
            </div>
            <p className="text-xs app-text-secondary mt-1">
              Microservicio NLP + Machine Learning con explicabilidad transparente. Paleta Oficial:{' '}
              <a
                href="https://coolors.co/2b2d42-8d99ae-edf2f4-ef233c-4361ee"
                target="_blank"
                rel="noopener noreferrer"
                className="font-mono text-xs font-bold text-[#4361ee] underline hover:text-[#3751d8]"
              >
                [Coolors: #2b2d42-#8d99ae-#edf2f4-#ef233c-#4361ee]
              </a>
            </p>
          </div>

          {/* Controles de Estado y Tema */}
          <div className="flex flex-wrap items-center gap-3">
            <span className="font-mono text-xs px-2.5 py-1 rounded bg-[#2b2d42] border border-[#8d99ae] text-[#edf2f4] flex items-center gap-1.5">
              <span
                className={`w-2 h-2 rounded-full ${
                  backendStatus.startsWith('UP') ? 'bg-green-400' : 'bg-[#ef233c]'
                }`}
              />
              API: {backendStatus}
            </span>

            <button
              type="button"
              onClick={toggleTheme}
              className="bg-[#2b2d42] text-[#edf2f4] hover:bg-[#1e2030] border border-[#8d99ae] font-medium text-xs px-3.5 py-2 rounded-md font-mono flex items-center gap-2"
            >
              {isLightMode ? (
                <>
                  <Moon className="w-3.5 h-3.5" />
                  <span>Modo Oscuro</span>
                </>
              ) : (
                <>
                  <Sun className="w-3.5 h-3.5" />
                  <span>Modo Claro</span>
                </>
              )}
            </button>
          </div>
        </header>

        {/* Barra de Navegación de Vistas */}
        <nav className="flex flex-wrap gap-2 border-b app-border pb-3">
          <button
            type="button"
            onClick={() => setActiveTab('analyzer')}
            className={`px-4 py-2 text-xs font-mono rounded-md flex items-center gap-2 border ${
              activeTab === 'analyzer'
                ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
            }`}
          >
            <Activity className="w-4 h-4" />
            01. Analizador SMS & Pipeline NLP
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('metrics')}
            className={`px-4 py-2 text-xs font-mono rounded-md flex items-center gap-2 border ${
              activeTab === 'metrics'
                ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
            }`}
          >
            <BarChart2 className="w-4 h-4" />
            02. Métricas y Benchmarking ML
          </button>

          <button
            type="button"
            onClick={() => setActiveTab('history')}
            className={`px-4 py-2 text-xs font-mono rounded-md flex items-center gap-2 border ${
              activeTab === 'history'
                ? 'bg-[#4361ee] text-white border-[#4361ee] font-bold'
                : 'bg-[#2b2d42] text-[#edf2f4] border-[#8d99ae] hover:bg-[#393c59]'
            }`}
          >
            <Database className="w-4 h-4" />
            03. Auditoría en PostgreSQL
          </button>
        </nav>

        {/* Contenido Dinámico de la Vista */}
        <main className="space-y-8">
          {activeTab === 'analyzer' && (
            <div className="space-y-8">
              <section>
                <div className="border-b app-border pb-2 mb-4">
                  <h2 className="text-xl font-semibold app-text-primary">
                    Analizador Forense de Mensajes SMS
                  </h2>
                  <p className="text-xs app-text-secondary">
                    Clasificación instantánea en memoria con probabilidades numéricas y nivel de riesgo.
                  </p>
                </div>
                <MessageAnalyzer onAnalyzeSuccess={handleMessageAnalyzed} />
              </section>

              <section>
                <NLPStepViewer currentText={analyzedText} />
              </section>
            </div>
          )}

          {activeTab === 'metrics' && <MetricsDashboard />}

          {activeTab === 'history' && (
            <HistoryAuditTable onSelectMessage={handleSelectFromHistory} />
          )}
        </main>
      </div>

      {/* Pie de Página Canónico */}
      <footer className="max-w-7xl mx-auto w-full mt-12 pt-6 border-t app-border text-xs app-text-muted flex flex-col sm:flex-row items-center justify-between gap-2 font-mono">
        <span>
          SMS Sentinel — Frontend React 18 + Vite [Puerto 3090]
        </span>
        <div className="flex items-center gap-3">
          <span className="text-[#4361ee] font-bold">Cero Degradados</span>
          <span>•</span>
          <span className="text-[#edf2f4]">Cero Animaciones</span>
          <span>•</span>
          <span className="text-[#8d99ae]">Design System Canónico</span>
        </div>
      </footer>
    </div>
  );
};
export default App;
