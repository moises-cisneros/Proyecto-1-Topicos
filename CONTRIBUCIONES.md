# Registro de Contribuciones del Proyecto (CONTRIBUCIONES.md)

> **Proyecto:** SMS Sentinel (Detección de Spam y Phishing en SMS mediante NLP y Machine Learning)  
> **Autor / Desarrollador:** Moises Cisneros  
> **Email en Git:** `moisescisnerosdl@gmail.com`  

---

## 1. Resumen de Cobertura de Capas del Sistema

Este registro documenta la autoría y el dominio técnico en cada una de las capas obligatorias de la arquitectura:

| Capa Técnica | Módulo / Directorio | Estado | Commits Clave |
| :--- | :--- | :---: | :--- |
| **Capa 1: Datos & EDA** | `data/`, `notebooks/01_eda.ipynb` | Implementado | `67836de`, `02a30da`, `9263b5e`, `2aa0ed2` |
| **Capa 2: Pipeline de NLP** | `src/nlp/` (normalizer, stopwords, tokenizer) | Implementado | `de1c006`, `796c7b9`, `aeb4c56`, `3094213` |
| **Capa 3: Modelado & ML** | `src/models/` (train, evaluate, .joblib) | Implementado | `6b78043`, `1f7f3c3`, `7aa9ded`, `310ecaf`, `d8ee8a8` |
| **Capa 4: Backend REST API** | `api/` (FastAPI, PostgreSQL, schemas) | Planificado | - |
| **Capa 5: Frontend UI & Explicabilidad** | `web/` (React, visor NLP, métricas) | Planificado | - |
| **Capa 6: DevOps, Testing & CI/CD** | `.github/` | Implementado | Configuración base y CI inicial |

---

## 2. Registro Granular de Commits

### 2.1 Fase 0: Configuración Base, Gobernanza y Herramientas de Calidad

Commits fundacionales en la rama `main` para establecer las bases de arquitectura, calidad de código y canal de integración continua:

| Hash | Rama | Tipo & Módulo | Descripción Técnica del Cambio | Decisión de Diseño & Alternativa Descartada |
| :--- | :---: | :--- | :--- | :--- |
| `c5145fb` | `main` | `chore` | Inicializar repositorio con `.gitignore`, licencia MIT, git hooks locales y herramientas de verificación. | **Decisión:** Configurar ignores estrictos, pre-commit checks y aislar dependencias transitorias. **Alternativa descartada:** Subir binarios, entornos `.env` o archivos de borradores al repositorio. |
| `b9c7806` | `main` | `docs` | Establecer arquitectura limpia hexagonal, especificación de diseño UI, mockups interactivos y normas de contribución. | **Decisión:** Documentar aislamiento de puertos (`3090`, `8090`, `5439`) y matriz semántica de diseño. **Alternativa descartada:** Codificar sin especificación formal. |
| `b207cc6` | `main` | `ci` | Configurar canal de integración continua en GitHub Actions, plantillas de issues/PRs y skills técnicas de verificación. | **Decisión:** Pipeline automatizado que valida sintaxis Python, tests y frontend. **Alternativa descartada:** Verificación manual propensa a omisiones. |
| `577a02a` | `main` | `docs(contribuciones)` | Inicializar registro de contribuciones del proyecto y mapa de historias de usuario. | **Decisión:** Trazabilidad commit a commit para auditoría de calidad de software. **Alternativa descartada:** Documentar contribuciones al final de memoria. |
| `7105603` | `main` | `chore(github)` | Incorporar sección de mapeo de archivos por arquitectura en plantilla de User Story. | **Decisión:** Exigir en cada issue la lista explícita de archivos a crear y modificar. **Alternativa descartada:** Issues ambiguas sin mapeo de archivos de arquitectura. |

---

### 2.2 Fases de Desarrollo: Historias de Usuario (HUs)

Registro de funcionalidades desarrolladas mediante ramas de trabajo (`feat/*`) e integradas a `main` a través de Pull Requests:

| Hash | Rama / PR | Issue Vinculada | Tipo & Módulo | Descripción Técnica del Cambio | Decisión de Diseño & Alternativa Descartada |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `67836de` | `feat/hu01-data-eda` | #1 | `feat(data)` | Descargar y estructurar dataset de SMS en español (5.572 muestras, 0 nulos). | **Decisión:** Utilizar corpus de dbarbedillo con columna text_es por contener el balance auténtico de spam y 0 nulos. **Alternativa descartada:** Gabrielaz/spamspa que requiere tokens LFS y falla en descarga anónima. |
| `02a30da` | `feat/hu01-data-eda` | #1 | `feat(data)` | Partición estratificada 80/20 reproducible con semilla fija 42 (`train.csv` y `test.csv`). | **Decisión:** Mantener split estratificado fijo con semilla 42 y congelar holdout test set. **Alternativa descartada:** Split aleatorio no reproducible que contamina el test set. |
| `9263b5e` | `feat/hu01-data-eda` | #1 | `docs(eda)` | Notebook interactivo `01_eda.ipynb` con análisis de clases, longitudes y vocabulario. | **Decisión:** Visualizar distribuciones KDE, boxplots y correlación de entidades (URLs/números) para justificar tokens sintéticos. **Alternativa descartada:** Entrenar modelos sin análisis exploratorio previo. |
| `2aa0ed2` | `feat/hu01-data-eda` | #1 | `test(data)` | Suite de pruebas de integridad de datos, ausencia de nulos y ratio 80/20 en pytest. | **Decisión:** Automatizar verificación de esquemas y proporciones estratificadas para CI. **Alternativa descartada:** Verificación manual de archivos CSV. |
| `de1c006` | `feat/hu02-nlp-pipeline` | #2 | `feat(nlp)` | Implementar normalizador con regex para enmascaramiento de `TOKEN_URL`, `TOKEN_TEL` y `TOKEN_NUM`. | **Decisión:** Enmascarar con tokens sintéticos para preservar la señal semántica del vector de ataque. **Alternativa descartada:** Borrar URLs, teléfonos y números por completo, destruyendo los predictores clave de phishing y spam. |
| `796c7b9` | `feat/hu02-nlp-pipeline` | #2 | `feat(nlp)` | Configurar lista de stopwords en español con whitelist contextual de urgencia y negaciones. | **Decisión:** Preservar negaciones ("no", "sin") y detonantes de urgencia ("urgente", "bloqueada", "ya") en la whitelist. **Alternativa descartada:** Aplicar stop words crudas de NLTK que eliminan la urgencia y alteran la polaridad del mensaje. |
| `aeb4c56` | `feat/hu02-nlp-pipeline` | #2 | `feat(nlp)` | Implementar tokenizador boundary-safe que respeta límites de palabras y tokens sintéticos. | **Decisión:** Regex unificada con frontera léxica para no fragmentar tokens sintéticos ni recortar sufijos en stemming. **Alternativa descartada:** Tokenización naive por split o regex estándar que rompe guiones bajos o stemmea tokens sintéticos. |
| `3094213` | `feat/hu02-nlp-pipeline` | #2 | `test(nlp)` | Añadir suite de 12 pruebas unitarias de normalización, entidades, stopwords y trazabilidad en pytest. | **Decisión:** Validar exhaustivamente cada transformación intermedia y casos de borde para blindar el componente ante regresiones. **Alternativa descartada:** Pruebas informales en scripts desechables sin aserciones automatizadas. |
| `6b78043` | `feat/hu03-model-training` | #3 | `feat(nlp)` | Benchmark experimental de Stemming vs. Lematización y N-gramas (1,1 vs 1,2) en `02_nlp_experiments.ipynb`. | **Decisión:** Evaluar métricas y latencia de inferencia empíricamente demostrando viabilidad de Snowball Stemming frente a sobrecosto de spaCy. **Alternativa descartada:** Elegir arbitrariamente lematización profunda sin medir la penalización de latencia de 15x en inferencia de SMS. |
| `1f7f3c3` | `feat/hu03-model-training` | #3 | `feat(ml)` | Implementar baseline Dummy y ensamblador `build_sms_pipeline` con `TfidfVectorizer` sublineal. | **Decisión:** Integrar preprocesamiento atómico en Pipeline para respetar el Principio de Pipeline Único desde la base. **Alternativa descartada:** Mantener preprocesamiento desacoplado fuera del pipeline de scikit-learn. |
| `7aa9ded` | `feat/hu03-model-training` | #3 | `feat(ml)` | Implementar módulo `evaluate.py` con métricas por clase, monitoreo de FPR y diagnóstico cualitativo de FP y FN. | **Decisión:** Auditar Falsos Positivos con diagnóstico de causa raíz para proteger mensajes legítimos contra falsas alarmas. **Alternativa descartada:** Reportar solo Accuracy global ocultando el impacto del desbalance de clases en SMS. |
| `310ecaf` | `feat/hu03-model-training` | #3 | `feat(ml)` | Script unificado de entrenamiento `train.py`, sintonía 5-Fold Stratified CV y serialización a `spam_detector_pipeline.joblib`. | **Decisión:** Seleccionar modelo de mayor F1-Macro y exportar métricas a `models/metrics.json` y binario listo para API. **Alternativa descartada:** Entrenar sin validación cruzada estratificada arriesgando sobreajuste en la partición de prueba. |
| `d8ee8a8` | `feat/hu03-model-training` | #3 | `test(ml)` | Añadir suite de 9 pruebas de reproducibilidad determinista, serialización joblib y validación de métricas en disco. | **Decisión:** Automatizar pruebas de carga en frío y validación de contrato de esquema en CI. **Alternativa descartada:** Pruebas manuales o asumir que la serialización en disco preserva el comportamiento sin aserciones. |
| *[Hash]* | `feat/hu04-api-inference` | #4 | `feat(api)` | Rutas FastAPI `/predict`, `/predict/batch`, `/nlp/debug` y `/metrics`. | **Decisión:** Exponer `/nlp/debug` para permitir explicabilidad paso a paso en el frontend. **Alternativa descartada:** Caja negra que solo devuelve 0 o 1. |
| *[Hash]* | `feat/hu05-db-audit` | #5 | `feat(db)` | Modelo SQLAlchemy `MessageAudit` y conexión a PostgreSQL en puerto 5439. | **Decisión:** Puerto 5439 para evitar colisión con Postgres local del host. **Alternativa descartada:** Base de datos en memoria sin persistencia de auditoría. |
| *[Hash]* | `feat/hu07-frontend-ui` | #7 | `feat(web)` | Interfaz React con formulario, semáforo de riesgo y visualizador paso a paso de NLP. | **Decisión:** Componente explicativo paso a paso. **Alternativa descartada:** Dashboard estático sin trazabilidad del preprocesamiento. |

---

## 3. Operatividad y Validación del Sistema

* **Trazabilidad y Autoría:** El 100% de los commits pertenecen a la cuenta configurada del autor, sin cuentas compartidas ni reescrituras destructivas de historial (`no force-push`).
* **Justificación de Modelos:** Racional teórico y matemático de selección y descarte de modelos de Machine Learning documentado en `ARCHITECTURE.md`.
* **Pruebas de Sensibilidad y Reconfiguración:** Pipeline modularizado con script de reentrenamiento unificado (`pnpm ml:train` o `python src/models/train.py`), permitiendo modificar stopwords, n-gramas o hiperparámetros y verificar el cambio de métricas en tiempo real.
