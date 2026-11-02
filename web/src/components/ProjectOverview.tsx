import React from 'react';
import {
  BrainCircuit,
  Database,
  FileCheck,
  Layers,
  Network,
  Scale,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export const ProjectOverview: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* 1. Misión Operativa y Arquitectura Empresarial */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <ShieldCheck className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              1. Topología del Sistema y Dominio de Ciberseguridad
            </h3>
            <p className="text-xs app-text-secondary">
              Pasarela de inspección forense para detección de Smishing, estafas bancarias y vectores de ingeniería social.
            </p>
          </div>
        </div>

        <p className="text-sm app-text-secondary leading-relaxed">
          <strong>SMS Sentinel</strong> implementa una arquitectura modular desacoplada de alto rendimiento (FastAPI + scikit-learn + PostgreSQL + React) diseñada para operar como pasarela de filtrado previo a la entrega en operadoras móviles o gateways corporativos. Analiza mensajes SMS en español garantizando inferencia en memoria en menos de 5 milisegundos con persistencia de auditoría inmutable.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1.5">
              <Zap className="w-4 h-4 text-[#4361ee]" />
              <h4 className="text-xs font-mono font-bold text-[#4361ee]">
                Inferencia Sub-5ms
              </h4>
            </div>
            <p className="text-xs app-text-secondary">
              Pipeline unificado serializado en binario atómico <code>.joblib</code> cargado en memoria de FastAPI durante el ciclo de vida <code>lifespan</code>.
            </p>
          </div>

          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1.5">
              <BrainCircuit className="w-4 h-4 text-[#ef233c]" />
              <h4 className="text-xs font-mono font-bold text-[#ef233c]">
                Vectores Sintéticos
              </h4>
            </div>
            <p className="text-xs app-text-secondary">
              Normalización con enmascaramiento regex (<code>TOKEN_URL</code>, <code>TOKEN_TEL</code>, <code>TOKEN_NUM</code>) que abstrae enlaces y remitentes efímeros.
            </p>
          </div>

          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <div className="flex items-center gap-2 mb-1.5">
              <Database className="w-4 h-4 text-green-400" />
              <h4 className="text-xs font-mono font-bold text-green-400">
                Auditoría Inmutable
              </h4>
            </div>
            <p className="text-xs app-text-secondary">
              Persistencia transaccional en PostgreSQL (puerto aislado 5439) con telemetría de latencia, probabilidades calibradas y nivel de riesgo.
            </p>
          </div>
        </div>
      </section>

      {/* 2. Pipeline de Procesamiento de Lenguaje Natural (NLP) */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <Layers className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              2. Especificación Técnica del Pipeline de NLP
            </h3>
            <p className="text-xs app-text-secondary">
              Transformación determinista empaquetada estrictamente en <code>sklearn.pipeline.Pipeline</code>.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
          <div className="p-4 rounded-lg border app-border bg-[#232537] space-y-2">
            <span className="text-[#4361ee] font-bold block">
              Fase 1: Normalización & Enmascaramiento Regex
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Conversión a minúsculas, remoción de tildes/diacríticos y sustitución determinista de URLs, números telefónicos y montos monetarios mediante tokens sintéticos. Preserva la señal de ataque sin sobreajustar a dominios específicos.
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537] space-y-2">
            <span className="text-[#4361ee] font-bold block">
              Fase 2: Tokenización Boundary-Safe
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Segmentación léxica con fronteras de palabras estrictas (<code>\b</code>) que respeta los guiones bajos internos de los tokens sintéticos, evitando su fragmentación o mutilación en etapas posteriores.
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537] space-y-2">
            <span className="text-[#4361ee] font-bold block">
              Fase 3: Stop Words con Whitelist Contextual
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Eliminación de conectores no informativos del español, preservando una whitelist estricta de negaciones (<code>no</code>, <code>sin</code>) y detonantes de urgencia (<code>urgente</code>, <code>bloqueada</code>, <code>ya</code>, <code>cuenta</code>).
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537] space-y-2">
            <span className="text-[#4361ee] font-bold block">
              Fase 4: Reducción Morfológica (Snowball Stemming)
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Lematización empíricamente evaluada frente a Snowball Stemming. Se seleccionó Snowball por ofrecer métricas F1 idénticas reduciendo la latencia de inferencia en 15x (evitando el sobrecosto pesado de spaCy en producción).
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537] space-y-2 md:col-span-2">
            <span className="text-[#4361ee] font-bold block">
              Fase 5: Vectorización TF-IDF Sublineal con N-gramas (1, 2)
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Matriz dispersa con <code>sublinear_tf=True</code> (escala logarítmica <code>1 + log(tf)</code>), rango de unigramas y bigramas para capturar colocaciones maliciosas (&quot;cuenta bloqueada&quot;, &quot;premio exclusivo&quot;), <code>max_features=5000</code> y <code>min_df=2</code>.
            </p>
          </div>
        </div>
      </section>

      {/* 3. Modelado Predictivo y Selección del Modelo */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <Scale className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              3. Benchmarking de Modelos y Criterio de Selección
            </h3>
            <p className="text-xs app-text-secondary">
              Comparativa empírica sobre partición holdout independiente (1.115 SMS) con 5-Fold Stratified CV.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs font-mono">
            <thead>
              <tr className="border-b app-border text-[#8d99ae]">
                <th className="py-2.5 px-3">Modelo Evaluado</th>
                <th className="py-2.5 px-3 text-center">Rol en Benchmark</th>
                <th className="py-2.5 px-3 text-right">Accuracy</th>
                <th className="py-2.5 px-3 text-right">F1-Macro</th>
                <th className="py-2.5 px-3 text-right">Recall (Spam)</th>
                <th className="py-2.5 px-3 text-center">Decisión Técnica</th>
              </tr>
            </thead>
            <tbody className="divide-y app-border">
              <tr>
                <td className="py-2.5 px-3 font-semibold text-[#8d99ae]">
                  Dummy Most Frequent
                </td>
                <td className="py-2.5 px-3 text-center">Baseline Cero-Valor</td>
                <td className="py-2.5 px-3 text-right">86.64%</td>
                <td className="py-2.5 px-3 text-right text-[#ef233c]">0.4642</td>
                <td className="py-2.5 px-3 text-right text-[#ef233c]">0.0%</td>
                <td className="py-2.5 px-3 text-center text-[#8d99ae]">Descartado (sin poder predictivo)</td>
              </tr>
              <tr>
                <td className="py-2.5 px-3 font-semibold app-text-primary">
                  Multinomial Naive Bayes (α=0.1)
                </td>
                <td className="py-2.5 px-3 text-center">Candidato Probabilístico</td>
                <td className="py-2.5 px-3 text-right">98.21%</td>
                <td className="py-2.5 px-3 text-right">0.9594</td>
                <td className="py-2.5 px-3 text-right">87.92%</td>
                <td className="py-2.5 px-3 text-center text-[#8d99ae]">Excelente FPR, menor Recall</td>
              </tr>
              <tr className="bg-[#4361ee]/10 font-bold">
                <td className="py-2.5 px-3 text-[#4361ee] flex items-center gap-1.5">
                  <FileCheck className="w-4 h-4 text-[#4361ee]" />
                  Logistic Regression (C=50.0)
                </td>
                <td className="py-2.5 px-3 text-center text-[#4361ee]">Modelo en Producción</td>
                <td className="py-2.5 px-3 text-right text-[#4361ee]">98.65%</td>
                <td className="py-2.5 px-3 text-right text-[#4361ee]">0.9709</td>
                <td className="py-2.5 px-3 text-right text-[#4361ee]">94.63%</td>
                <td className="py-2.5 px-3 text-center text-green-400">Seleccionado (Máximo F1 & Recall)</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4. Aislamiento de Red y Puertos */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <Network className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              4. Aislamiento de Red y Arquitectura de Contenedores
            </h3>
            <p className="text-xs app-text-secondary">
              Puertos explícitamente configurados para evitar colisiones con servicios locales del host.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 font-mono text-xs">
          <div className="p-4 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">Frontend React (Vite)</span>
            <span className="text-sm font-bold text-[#edf2f4]">Puerto 3090</span>
            <p className="font-sans text-xs app-text-secondary mt-1">
              Servidor web estático / Nginx con proxies inversos hacia la API y Tailwind CSS canónico.
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">Backend REST (FastAPI)</span>
            <span className="text-sm font-bold text-[#edf2f4]">Puerto 8090</span>
            <p className="font-sans text-xs app-text-secondary mt-1">
              Uvicorn ASGI asíncrono, CORS configurado, Pydantic v2 y endpoints OpenAPI nativos.
            </p>
          </div>

          <div className="p-4 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">Base de Datos (PostgreSQL)</span>
            <span className="text-sm font-bold text-[#edf2f4]">Puerto 5439</span>
            <p className="font-sans text-xs app-text-secondary mt-1">
              PostgreSQL 16 Alpine con connection pooling en SQLAlchemy y esquema inmutable de auditoría.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
