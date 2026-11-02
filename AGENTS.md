# Directrices para Agentes y Desarrolladores (AGENTS.md)

Este repositorio contiene el sistema **SMS Sentinel (Detección de Spam y Phishing en SMS mediante NLP y Machine Learning)**. Todos los agentes, subagentes o procesos automatizados que operen en este espacio de trabajo deben adherirse rigurosamente a las siguientes directivas de arquitectura y calidad de software:

## 1. Reglas de Código y Control de Versiones

* **Estándar de Commits e Identidad:** Utilizar **Conventional Commits** exclusivamente (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`). Los commits deben estar firmados por un autor humano válido con nombre y correo configurados en su git local/global. Prohibición absoluta de firmas o atribuciones artificiales (`Co-Authored-By`, `Antigravity`, `Claude`, `Cursor`, etc.) en commits, PRs o merges.
* **Integridad de Documentación:** Preservar y enriquecer comentarios técnicos, docstrings y especificaciones funcionales en `docs/`.
* **Memoria Persistente (Engram):** Registrar proactivamente en Engram (`mem_save`) cualquier decisión arquitectónica, hallazgo experimental o convención de código adoptada.
* **Inteligencia de Código (CodeGraph):** Consultar CodeGraph antes de realizar búsquedas textuales masivas para mapear dependencias y símbolos del proyecto.

## 2. Restricciones Arquitectónicas Fundamentales

* **Principio de Pipeline Único:** El preprocesamiento de NLP (normalización con enmascaramiento regex de URLs/teléfonos/números, stopwords contextualizadas, lematización/stemming y TF-IDF sublineal) debe empaquetarse estrictamente en un `sklearn.pipeline.Pipeline` serializado en `.joblib`. El backend FastAPI **nunca** debe reimplementar el preprocesamiento manualmente.
* **Determinismo y Reproducibilidad:** Todo script de modelado y entrenamiento debe fijar semillas aleatorias (`random_state=42`) y utilizar particiones estratificadas fijas (80/20).
* **Aislamiento de Puertos de Red:** Respetar los puertos asignados para evitar colisiones:
  * Frontend Web: `3090`
  * Backend API: `8090`
  * Base de Datos PostgreSQL: `5439`

## 3. Skills Especializadas Disponibles en `.agents/skills/`

1. `nlp-text-pipeline`: Especificación técnica y validación del preprocesamiento de texto en español (regex, tokens, stopwords con whitelist, stemming vs lematización, n-gramas, TF-IDF y serialización en Pipeline).
2. `ml-model-evaluation`: Especificación técnica y benchmarking de modelos de machine learning (Baseline DummyClassifier, MultinomialNB, LogisticRegression, sintonía con 5-Fold Stratified CV, métricas completas y análisis de errores).
3. `api-service-integration`: Especificación de integración del servicio REST (FastAPI), persistencia de auditoría (PostgreSQL), inspector visual de NLP en frontend (React) y pruebas de sensibilidad ante reconfiguraciones de parámetros.
4. `contributions-tracker`: Especificación técnica y validación automatizada de registro de contribuciones y justificación de decisiones en CONTRIBUCIONES.md.
