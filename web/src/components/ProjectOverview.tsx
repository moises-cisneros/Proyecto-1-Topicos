import React from 'react';
import {
  BrainCircuit,
  Database,
  Layers,
  Shield,
} from 'lucide-react';

export const ProjectOverview: React.FC = () => {
  return (
    <div className="space-y-8 max-w-5xl">
      {/* 1. Visión y Propósito en el Mundo Real */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <Shield className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              1. Propósito y Aplicación en el Mundo Real
            </h3>
            <p className="text-xs app-text-secondary">
              Protección de usuarios contra ingeniería social y estafas bancarias en mensajería móvil.
            </p>
          </div>
        </div>

        <p className="text-sm app-text-secondary leading-relaxed">
          <strong>SMS Sentinel</strong> es una solución de ciberseguridad diseñada para operar a nivel de
          cliente o pasarela corporativa. El sistema analiza mensajes de texto SMS en español para
          clasificar instantáneamente si constituyen comunicaciones legítimas (<strong>Ham</strong>) o
          vectores maliciosos de suplantación de identidad (<strong>Phishing / Smishing</strong>).
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-2">
          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <h4 className="text-xs font-mono font-bold text-[#4361ee] mb-1">
              Vectores Dinámicos
            </h4>
            <p className="text-xs app-text-secondary">
              Detección de URLs acortadas, enlaces maliciosos, teléfonos de contacto sospechosos y montos financieros mediante tokens sintéticos.
            </p>
          </div>

          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <h4 className="text-xs font-mono font-bold text-[#4361ee] mb-1">
              Inferencia en Memoria
            </h4>
            <p className="text-xs app-text-secondary">
              Respuesta en menos de 5 milisegundos gracias al preprocesamiento unificado y serialización atómica en scikit-learn.
            </p>
          </div>

          <div className="app-card-subtle border app-border p-4 rounded-lg">
            <h4 className="text-xs font-mono font-bold text-[#4361ee] mb-1">
              Auditoría Forense
            </h4>
            <p className="text-xs app-text-secondary">
              Persistencia inmutable de cada consulta con probabilidades calibradas, tokens y telemetría en base de datos PostgreSQL.
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
              2. Arquitectura del Pipeline de NLP
            </h3>
            <p className="text-xs app-text-secondary">
              Transformación determinista de texto adaptada a la morfología y semántica del español.
            </p>
          </div>
        </div>

        <div className="space-y-3 font-mono text-xs">
          <div className="p-3.5 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">
              Fase 1: Normalización y Enmascaramiento Regex
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Conversión a minúsculas, eliminación de tildes y diacríticos, y sustitución regex de
              entidades por tokens sintéticos (<code className="text-[#ef233c]">TOKEN_URL</code>,{' '}
              <code className="text-[#4361ee]">TOKEN_TEL</code>,{' '}
              <code className="text-[#edf2f4]">TOKEN_NUM</code>). Permite capturar la presencia del vector sin sobreajustar a dominios específicos.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">
              Fase 2: Tokenización Boundary-Safe
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Segmentación léxica con frontera de palabras (<code className="text-[#edf2f4]">\b</code>) que respeta los tokens sintéticos sin fragmentarlos por guiones bajos.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">
              Fase 3: Filtrado de Stop Words con Whitelist Contextual
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Eliminación de palabras vacías del español, preservando términos clave de polaridad y
              urgencia bancaria: negaciones (<code className="text-[#edf2f4]">no</code>,{' '}
              <code className="text-[#edf2f4]">sin</code>) y detonantes (<code className="text-[#edf2f4]">urgente</code>,{' '}
              <code className="text-[#edf2f4]">bloqueada</code>, <code className="text-[#edf2f4]">alerta</code>).
            </p>
          </div>

          <div className="p-3.5 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">
              Fase 4: Reducción Morfológica (Snowball Stemming)
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Reducción a raíces léxicas optimizada en latencia para SMS en español, preservando la integridad de los tokens sintéticos.
            </p>
          </div>

          <div className="p-3.5 rounded-lg border app-border bg-[#232537]">
            <span className="text-[#4361ee] font-bold block mb-1">
              Fase 5: Extracción de Características TF-IDF con N-Gramas
            </span>
            <p className="app-text-secondary font-sans text-xs">
              Vectorización unigramas + bigramas <code className="text-[#edf2f4]">(1, 2)</code> con
              ponderación sublineal <code className="text-[#edf2f4]">1 + log(tf)</code> para mitigar la repetición artificial en textos breves.
            </p>
          </div>
        </div>
      </section>

      {/* 3. Análisis Racional de los 8 Modelos de Machine Learning */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <BrainCircuit className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              3. Justificación y Racional de Selección de Modelos
            </h3>
            <p className="text-xs app-text-secondary">
              Evaluación crítica de los 8 modelos del temario para clasificación de texto.
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left font-mono text-xs border app-border">
            <thead className="bg-[#232537] border-b app-border text-[#edf2f4]">
              <tr>
                <th className="p-3">Modelo</th>
                <th className="p-3">Estado</th>
                <th className="p-3">Racional Técnico / Justificación</th>
              </tr>
            </thead>
            <tbody className="divide-y app-border font-sans">
              <tr>
                <td className="p-3 font-mono font-bold text-[#edf2f4]">DummyClassifier</td>
                <td className="p-3 font-mono text-yellow-400">Baseline</td>
                <td className="p-3 text-xs app-text-secondary">
                  Predice siempre la clase mayoritaria (<code className="text-[#8d99ae]">ham</code>). Demuestra el valor agregado real del modelado ante el desbalance natural de SMS.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-green-400">Multinomial Naive Bayes</td>
                <td className="p-3 font-mono text-green-400 font-bold">Producción (Ganador)</td>
                <td className="p-3 text-xs app-text-secondary">
                  Estándar por excelencia para texto y frecuencias TF-IDF. Mínima memoria, entrenamiento ultrarrápido y excelente robustez con alta dimensionalidad dispersa.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-blue-400">Logistic Regression</td>
                <td className="p-3 font-mono text-blue-400 font-bold">Challenger</td>
                <td className="p-3 text-xs app-text-secondary">
                  Frontera de decisión lineal probabilística con función sigmoide. Coeficientes altamente interpretables que indican el peso exacto de cada término de spam.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-[#8d99ae]">Random Forest / XGBoost</td>
                <td className="p-3 font-mono text-[#8d99ae]">Benchmark</td>
                <td className="p-3 text-xs app-text-secondary">
                  Modelos de ensamble no lineales. Tienen buen rendimiento pero su inferencia y tamaño en disco (<code className="text-[#8d99ae]">&gt; 50 MB</code>) penalizan la latencia de respuesta frente a modelos lineales.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-[#ef233c]">Regresión Lineal</td>
                <td className="p-3 font-mono text-[#ef233c]">Descartado</td>
                <td className="p-3 text-xs app-text-secondary">
                  Inadecuado por diseño: es una tarea de clasificación categórica binaria y no de regresión continua.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-[#ef233c]">K-Means</td>
                <td className="p-3 font-mono text-[#ef233c]">Descartado</td>
                <td className="p-3 text-xs app-text-secondary">
                  Algoritmo no supervisado con distancia euclidiana susceptible a la maldición de la dimensionalidad en TF-IDF.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-[#ef233c]">KNN (K-Nearest)</td>
                <td className="p-3 font-mono text-[#ef233c]">Descartado</td>
                <td className="p-3 text-xs app-text-secondary">
                  Algoritmo perezoso sin fase de entrenamiento: latencia <code className="text-[#ef233c]">O(N·D)</code> inviable para APIs en tiempo real con miles de features.
                </td>
              </tr>
              <tr>
                <td className="p-3 font-mono font-bold text-[#ef233c]">Árbol de Decisión (CART)</td>
                <td className="p-3 font-mono text-[#ef233c]">Descartado</td>
                <td className="p-3 text-xs app-text-secondary">
                  Alta varianza y sobreajuste severo: memoriza palabras aisladas sin capturar la combinación distribuida de vocabulario en SMS.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      {/* 4. Dataset y Protocolo Experimental */}
      <section className="app-card border rounded-xl p-6 space-y-4">
        <div className="flex items-center gap-3 border-b app-border pb-3">
          <Database className="w-6 h-6 text-[#4361ee]" />
          <div>
            <h3 className="text-lg font-bold app-text-primary">
              4. Dataset, División Estratificada y Protocolo
            </h3>
            <p className="text-xs app-text-secondary">
              Garantía de rigor científico y reproducibilidad determinista.
            </p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="app-card-subtle border app-border p-4 rounded-lg space-y-2">
            <h4 className="font-mono font-bold app-text-primary">Estructura del Corpus</h4>
            <ul className="space-y-1.5 app-text-secondary">
              <li>• <strong>Total de muestras:</strong> 5.572 mensajes SMS en español.</li>
              <li>• <strong>Distribución:</strong> ~86.6% Legítimos (Ham) / ~13.4% Spam/Phishing.</li>
              <li>• <strong>Valores nulos:</strong> 0 registros faltantes en texto y etiquetas.</li>
            </ul>
          </div>

          <div className="app-card-subtle border app-border p-4 rounded-lg space-y-2">
            <h4 className="font-mono font-bold app-text-primary">Partición y Validación</h4>
            <ul className="space-y-1.5 app-text-secondary">
              <li>• <strong>Split 80/20:</strong> 4.457 muestras de entrenamiento / 1.115 de prueba holdout.</li>
              <li>• <strong>Estratificación estricta:</strong> Idéntica proporción de spam en train y test.</li>
              <li>• <strong>Semilla determinista:</strong> <code className="text-[#4361ee]">random_state=42</code> en todas las fases.</li>
              <li>• <strong>Validación Cruzada:</strong> 5-Fold Stratified CV para ajuste de hiperparámetros.</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
};
