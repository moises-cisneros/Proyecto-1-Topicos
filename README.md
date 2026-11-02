# SMS Sentinel

> **Sistema Inteligente de Detección y Clasificación de Spam y Phishing en Mensajería SMS mediante NLP y Machine Learning.**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-61DAFB.svg)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791.svg)](https://www.postgresql.org/)

---

## 1. Visión General del Proyecto

**SMS Sentinel** es una plataforma integral diseñada para la detección, clasificación y auditoría en tiempo real de mensajes SMS fraudulentos (*smishing*) y no solicitados (*spam*), optimizada específicamente para textos en español.

El sistema resuelve el desafío de procesar mensajes breves, con lenguaje coloquial, errores ortográficos y vectores de ataque dinámicos (enlaces acortados, teléfonos de contacto, urgencia fabricada), integrando un pipeline modular de Procesamiento de Lenguaje Natural (NLP), modelos supervisados de Machine Learning y una interfaz de usuario explicable e interactiva.

---

## 2. Arquitectura del Sistema

El proyecto sigue una arquitectura desacoplada basada en microservicios contenerizados:

```
                      +-----------------------------+
                      |       Cliente / Web UI      |
                      |   React + TypeScript (3090) |
                      +--------------+--------------+
                                     |
                                     | REST (JSON)
                                     v
                      +-----------------------------+
                      |         API Gateway         |
                      |        FastAPI (8090)       |
                      +--------------+--------------+
                                     |
            +------------------------+------------------------+
            |                                                 |
            v                                                 v
+-----------------------+                         +-----------------------+
|  NLP & ML Pipeline    |                         |  Capa de Persistencia  |
|  - Preprocesamiento   |                         |  PostgreSQL (5439)    |
|  - Extracción TF-IDF  |                         |  - Auditoría de logs  |
|  - Clasificador Joblib|                         |  - Historial análisis |
+-----------------------+                         +-----------------------+
```

### Componentes Clave

1. **Frontend (React + Vite + TypeScript):** Interfaz analítica en puerto `3090` que ofrece:
   - Formulario de inferencia en tiempo real con indicador de nivel de riesgo.
   - Visor explicable paso a paso de las transformaciones del texto (NLP Debugger).
   - Panel de métricas con matrices de confusión y comparativas de rendimiento.
   - Historial de consultas auditadas.
2. **Backend de Inferencia (FastAPI):** Servicio REST en puerto `8090` con esquemas Pydantic, documentación interactiva OpenAPI/Swagger, y manejo estructurado de errores.
3. **Pipeline de NLP & Inferencia:** Serializado de forma atómica en un único `sklearn.pipeline.Pipeline` (`.joblib`), garantizando que la inferencia utilice exactamente la misma lógica de transformación que el entrenamiento.
4. **Base de Datos (PostgreSQL):** Instancia relacional en puerto `5439` para persistencia del historial de auditoría y predicciones.

---

## 3. Dataset y Protocolo de Preparación

El sistema se entrena y valida sobre un corpus real y representativo de mensajería SMS en español, estructurado bajo un protocolo de preparación determinista y auditable:

* **Repositorio y Enlace Oficial:** [`dbarbedillo/SMS_Spam_Multilingual_Collection_Dataset`](https://huggingface.co/datasets/dbarbedillo/SMS_Spam_Multilingual_Collection_Dataset) en la plataforma Hugging Face.
* **Origen Académico:** Derivado y traducido al español a partir del referente internacional *SMS Spam Collection Dataset*, compilado por Tiago A. Almeida y José María Gómez Hidalgo en el [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection).
* **Licencia:** Abierta para fines académicos y de investigación (Creative Commons Attribution 4.0 / Public Domain).
* **Volumen Total:** 5.572 mensajes etiquetados en español sin valores nulos ni duplicados residuales.
  * **Comunicaciones Legítimas (`ham`):** 4.827 registros (86.63%)
  * **Comunicaciones Maliciosas (`spam`):** 745 registros (13.37%)

### Pasos de Preparación y Aislamiento de Datos

1. **Extracción Lingüística:** Del corpus multilingüe se filtró la columna `text_es` como texto del mensaje (`text`) y la clasificación binaria (`label`: `ham` / `spam`), generando el archivo crudo `data/raw/sms_spanish.csv`.
2. **Partición Estratificada y Determinista (80/20):** Mediante el script automatizado `scripts/prepare_data.py` (ejecutable vía `pnpm data:prepare`), se aplicó una partición estratificada fijando la semilla aleatoria (`random_state=42`) para preservar la proporción de desbalance en ambas divisiones:
   * **Entrenamiento (`data/processed/train.csv`):** 4.457 muestras (3.861 `ham` [86.63%], 596 `spam` [13.37%]).
   * **Evaluación Holdout (`data/processed/test.csv`):** 1.115 muestras (966 `ham` [86.64%], 149 `spam` [13.36%]).
3. **Prevención de Fuga de Datos (*No Data Leakage*):** El conjunto de prueba `test.csv` permanece estrictamente congelado y aislado: ningún paso de normalización, extracción de vocabulario TF-IDF o sintonía de hiperparámetros tiene visibilidad sobre él, utilizándose únicamente para la evaluación final en frío.

---

## 4. Pipeline de Procesamiento de Lenguaje Natural (NLP)

El pipeline de preprocesamiento se compone de 6 etapas deterministas y reproducibles:

```
[ Texto Crudo ]
       |
       v
(1) Normalización & Enmascaramiento Regex
    ├── URLs -> TOKEN_URL
    ├── Teléfonos -> TOKEN_TEL
    └── Montos/Números -> TOKEN_NUM
       |
       v
(2) Tokenización Limpia
       |
       v
(3) Filtrado de Stop Words con Preservación de Contexto
    └── Conservación selectiva de detonantes de urgencia ("urgente", "ya") y negaciones ("no", "sin")
       |
       v
(4) Normalización Morfológica Dual (Stemming vs. Lematización)
    ├── Snowball Stemmer: Reducción algorítmica de sufijos para máxima velocidad (< 2 ms)
    └── Lematización Canónica ES: Reducción flexiva a lema de diccionario ("bloquear", "ganar", "cuenta")
       |
       v
(5) Extracción de N-Gramas
    └── Unigramas + Bigramas (captura patrones como "cuenta bloqueada", "haga clic")
       |
       v
(6) Vectorización TF-IDF
    └── Ponderación sublineal (sublinear_tf=True), poda de vocabulario (min_df, max_features)
       |
       v
[ Vector de Características ] -> Modelo Predictivo
```

---

## 5. Modelos de Machine Learning y Evaluación

El sistema implementa y compara de forma empírica tres aproximaciones:

| Modelo | Rol | Justificación Técnica |
| :--- | :--- | :--- |
| **DummyClassifier** | Línea Base (*Baseline*) | Estrategia de clase mayoritaria (`most_frequent`) para medir el valor agregado real del modelado. |
| **Multinomial Naive Bayes** | Modelo Challenger | Alta efectividad con representaciones dispersas TF-IDF, baja latencia y robustez en textos breves. Alisado de Laplace $\alpha$. |
| **Regresión Logística** | Modelo Ganador (Producción) | Frontera de decisión lineal calibrada, interpretabilidad directa de coeficientes e hiperparámetro de regularización $C=50.0$. |

### Protocolo de Evaluación

- **Partición:** División estratificada 80/20 (`random_state=42`) manteniendo proporción `ham`/`spam`.
- **Validación Cruzada:** 5-Fold Stratified K-Fold sobre el conjunto de entrenamiento para la sintonía de hiperparámetros.
- **Métricas:** Matriz de Confusión, Precisión, Exhaustividad (Recall), F1-Score (clase spam y macro) y Tasa de Falsos Positivos (para prevenir el bloqueo de mensajes legítimos).
- **Diagnóstico de Errores:** Análisis cualitativo sistemático de Falsos Positivos y Falsos Negativos para identificar casos de borde y vocabulario no observado.

---

## 6. Referencia de Endpoints API

La API REST expone los siguientes puntos de entrada documentados y tipados con Pydantic v2:

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/predict` | Clasifica un mensaje SMS individual, retornando etiqueta, probabilidad calibrada y nivel de riesgo con persistencia inmutable en PostgreSQL. |
| `POST` | `/predict/batch` | Clasifica lotes de mensajes en formato JSON con sumario estadístico agregado. |
| `POST` | `/predict/batch/csv` | Ingesta masiva multipart/form-data de archivos CSV para auditorías de alto volumen. |
| `POST` | `/nlp/debug` | Retorna el desglose paso a paso de las 5 transformaciones de NLP y pesos de características TF-IDF para explicabilidad forense. |
| `GET` | `/metrics` | Retorna las métricas comparativas del benchmark (Dummy, Naive Bayes, Regresión Logística) y sintonización de hiperparámetros. |
| `GET` | `/history` | Consulta el registro histórico paginado (`limit`, `offset`) de clasificaciones auditadas en PostgreSQL. |
| `POST` | `/audit/{audit_id}/feedback` | Registra retroalimentación humana de analistas (Active Learning) para capturar falsos positivos o falsos negativos. |
| `GET` | `/health` | Chequeo de salud del servicio, disponibilidad de modelo en memoria RAM y conexión a la base de datos. |

---

## 7. Estructura del Repositorio

El proyecto sigue una arquitectura modular en monorepo bajo `packages/` con desacoplamiento estricto:

```
SMS-Sentinel/
├── packages/
│   ├── api/                       # Paquete Microservicio REST API (FastAPI)
│   │   ├── database.py            # Conexión SQLAlchemy, connection pooling y degradación elegante
│   │   ├── models_db.py           # Modelo ORM MessageAudit para PostgreSQL
│   │   ├── schemas.py             # Esquemas Pydantic v2 (Input/Output estricto, HTTP 422)
│   │   ├── Dockerfile             # Imagen Docker para el backend
│   │   ├── requirements.txt       # Dependencias de producción de la API
│   │   └── main.py                # Aplicación FastAPI, ciclo de vida lifespan y rutas
│   ├── pipeline/                  # Paquete Motor de NLP y Machine Learning
│   │   ├── nlp/                   # Preprocesamiento de texto en español
│   │   │   ├── normalizer.py      # Normalización y enmascaramiento regex (TOKEN_URL, TOKEN_TEL, TOKEN_NUM)
│   │   │   ├── stopwords_es.py    # Stop words con whitelist contextual de urgencia y negaciones
│   │   │   ├── tokenizer.py       # Tokenizador boundary-safe con fronteras de palabra (\b)
│   │   │   └── pipeline_builder.py# Ensamblador del Pipeline único de scikit-learn
│   │   └── models/                # Modelado predictivo y evaluación
│   │       ├── train.py           # Script unificado con 5-Fold Stratified CV, grid search y modo --fast
│   │       └── evaluate.py        # Generación de matriz de confusión, métricas y análisis de errores
│   └── web/                       # Paquete Frontend Web (React 18 + TypeScript + Vite)
│       ├── src/components/        # Componentes UI (MessageAnalyzer, NLPStepViewer, MetricsDashboard, BatchAnalyzer)
│       ├── src/services/          # Clientes API HTTP (Axios / Fetch)
│       ├── src/styles/tokens.css  # Tokens de diseño y paleta canónica
│       ├── nginx.conf             # Servidor Nginx para contenedor web
│       ├── Dockerfile             # Imagen Docker multi-stage para frontend
│       └── package.json           # Dependencias y scripts de Vite
├── resources/                     # Recursos desacoplados de la aplicación
│   ├── example/                   # Muestras CSV y JSON de prueba (cero datos hardcodeados en código)
│   │   ├── samples.json           # Ejemplos predeterminados de SMS legítimos y fraudulentos
│   │   └── batch_samples.csv      # Dataset de prueba para ingesta masiva CSV
│   └── mockups/                   # Mockups estáticos de diseño
├── notebooks/                     # Experimentación reproducible y análisis
│   ├── 01_eda.ipynb               # Análisis exploratorio de datos, distribuciones y vocabulario
│   ├── 02_nlp_experiments.ipynb   # Benchmarking: Stemming vs Lematización y N-gramas
│   └── 03_model_training.ipynb    # Ajuste de hiperparámetros, curvas y análisis de matrices
├── data/                          # Almacenamiento local de datos
│   ├── raw/sms_spanish.csv        # Dataset fuente etiquetado en español (5.572 registros)
│   └── processed/                 # Particiones estratificadas fijas (train.csv y test.csv 80/20)
├── models/                        # Artefactos serializados generados
│   ├── spam_detector_pipeline.joblib # Pipeline reproducible empaquetado para producción
│   └── metrics.json               # Telemetría del benchmark de evaluación holdout
├── docs/                          # Documentación formal e informes
│   ├── informe_tecnico.md         # Informe técnico completo del proyecto
│   ├── presentacion.md            # Diapositivas en formato Marp Markdown
│   ├── presentacion_sms_sentinel.pptx # Presentación corporativa PowerPoint (10 slides)
│   ├── presentacion_sms_sentinel_light.pptx # Deck tema claro con notas del orador
│   ├── presentacion_sms_sentinel_dark.pptx  # Deck tema oscuro con notas del orador
│   └── internal/                  # Especificaciones internas y rúbrica oficial (Proyecto_Integrador.md)
├── scripts/                       # Utilidades de automatización y runners DX
│   ├── generate_presentation.py  # Generador de diapositivas PPTX con python-pptx
│   ├── generate_presentation_visuals.py # Generador de visuales de alta resolución
│   ├── run_api.cjs                # Runner de API con resolución automática de .venv
│   └── run_python.cjs             # Runner universal de Python para scripts monorepo
├── tests/                         # Suite completa de pruebas automatizadas en pytest
├── docker-compose.yml             # Orquestación de contenedores (Web 3090, API 8090, DB 5439)
├── ARCHITECTURE.md                # Especificación técnica de arquitectura y paquetes
├── CONTRIBUCIONES.md              # Registro detallado de autoría y trazabilidad de commits
├── LICENSE                        # Licencia MIT
└── README.md                      # Documentación principal
```

---

## 8. Puesta en Marcha (Quickstart)

### Configuración de Variables de Entorno

Copiar la plantilla de configuración predeterminada con los puertos aislados:

```bash
cp .env.example .env
```

| Servicio | Puerto Host (Aislado) | Puerto Interno Contenedor | Descripción |
| :--- | :---: | :---: | :--- |
| **Frontend Web (React/Vite)** | `3090` | `80` | Interfaz gráfica con visor de NLP y telemetría de riesgo. |
| **Backend REST API (FastAPI)** | `8090` | `8000` | Inferencia de SMS, endpoints `/predict`, `/nlp/debug`, Swagger UI. |
| **PostgreSQL** | `5439` | `5432` | Base de datos relacional para auditoría forense inmutable. |

---

### Opción A: Despliegue con Docker Compose (Recomendado)

Inicia todos los servicios con puertos mapeados, redes puente y healthchecks automatizados con un único comando:

```bash
# Iniciar servicios en segundo plano con reconstrucción
pnpm docker:up
# o directamente con Docker Compose:
docker compose up --build -d
```

- **Frontend Web UI:** [http://localhost:3090](http://localhost:3090)
- **API Swagger / OpenAPI:** [http://localhost:8090/docs](http://localhost:8090/docs)
- **Diagnóstico de Salud (/health):** [http://localhost:8090/health](http://localhost:8090/health)
- **Base de Datos PostgreSQL:** `localhost:5439`

Para consultar los logs o detener la infraestructura:

```bash
pnpm docker:logs     # Ver logs en vivo
pnpm docker:down     # Detener y remover contenedores
```

---

### Opción B: Ejecución Local Monorepo (pnpm + Python)

Gracias a la centralización de scripts en el `package.json` raíz y el espacio de trabajo pnpm:

```bash
# 1. Instalar dependencias web desde la raíz
pnpm install

# 2. Iniciar el frontend en desarrollo (puerto 3090)
pnpm dev

# 3. Iniciar el backend FastAPI en desarrollo (puerto 8090)
pnpm api:dev

# 4. Preparar particiones estratificadas desde el dataset crudo
pnpm data:prepare

# 5. Reentrenar el modelo de Machine Learning
pnpm ml:train        # Entrenamiento completo con 5-Fold Stratified CV
pnpm ml:train:fast   # Reentrenamiento rápido (< 50 segundos) para ensayos de sensibilidad
pnpm ml:train:lemmatize # Ensayo con lematización canónica en español

# 6. Generar diapositivas corporativas de presentación (.pptx y .md)
pnpm slides:generate

# 7. Ejecutar la suite completa de pruebas automatizadas
pnpm test
```

---

## 9. Presentación Ejecutiva y Diapositivas

El proyecto incluye diapositivas profesionales en formato panorámico 16:9 generadas mediante código determinista automatizado:

- **Presentación PowerPoint (.pptx):** [docs/presentacion_sms_sentinel.pptx](docs/presentacion_sms_sentinel.pptx) (10 diapositivas corporativas con métricas, diagramas de arquitectura, visuales de explicabilidad y tabla de benchmarking).
- **Variantes de Tema Dual (.pptx):**
  - Tema Claro: [docs/presentacion_sms_sentinel_light.pptx](docs/presentacion_sms_sentinel_light.pptx) (con notas detalladas del orador para cada diapositiva).
  - Tema Oscuro: [docs/presentacion_sms_sentinel_dark.pptx](docs/presentacion_sms_sentinel_dark.pptx) (con notas detalladas del orador para cada diapositiva).
- **Presentación Marp Markdown (.md):** [docs/presentacion.md](docs/presentacion.md) (previsualizable y exportable a PDF/HTML directamente en Visual Studio Code con la extensión Marp).
- **Script Generador:** `scripts/generate_presentation.py` (`pnpm slides:generate`).

---

## 10. Ensayos de Reconfiguración y Sensibilidad de Parámetros en Vivo

La arquitectura modular permite modificar parámetros del pipeline y verificar el cambio en inferencia en menos de 2 minutos sin romper contratos de API:

1. **Ajuste Léxico de Stop Words:**
   - Modificar o incorporar términos en `packages/pipeline/nlp/stopwords_es.py`.
   - Ejecutar `pnpm ml:train:fast`.
   - El artefacto `.joblib` se actualiza de forma atómica y `/nlp/debug` refleja la nueva segmentación en tiempo real.
2. **Modificación de N-Gramas:**
   - Alternar entre unigramas `(1, 1)` y bigramas `(1, 2)` en `packages/pipeline/nlp/pipeline_builder.py` para analizar la variación de dimensionalidad del vocabulario TF-IDF.
3. **Calibración de Umbrales de Riesgo:**
   - Ajustar los umbrales de decisión (`0.35` y `0.50`) en `packages/api/main.py` para adaptar la sensibilidad del semáforo de riesgo ante escenarios de alta sospecha.
4. **Verificación Automatizada de Sensibilidad:**
   - Ejecutar la suite dedicada:

     ```bash
     pytest tests/test_live_reconfiguration.py -v
     ```

---

## 11. Calidad de Código y Estándares de Contribución

- **Commits Convencionales:** Se adhiere rigurosamente al estándar [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- **Identidad de Autor:** 100% de los commits y registros de Git atribuidos al autor humano configurado (`moises-cisneros` / `moisescisnerosdl@gmail.com`).
- **Pipeline Determinista:** Semillas fijadas a `random_state=42` en todas las etapas estocásticas y particiones 80/20.
- **Validación Automática:** Scripts de validación previa disponibles en `scripts/pre_commit_check.ps1`.
- **Trazabilidad:** Archivo [CONTRIBUCIONES.md](CONTRIBUCIONES.md) sincronizado con el historial de commits.

---

## 12. Declaración de Cumplimiento de la Consigna y Asistencia de IA

Conforme a las directrices de la Sección 10 de la consigna oficial del Proyecto Integrador (*Proyecto_Integrador.md*):

* **Autoría y Responsabilidad Técnica:** La concepción de la arquitectura, diseño del pipeline de NLP, selección matemática de modelos de machine learning, implementación de endpoints en FastAPI y desarrollo de la consola React han sido dirigidos y validados integralmente por el autor (`moises-cisneros`).
* **Uso de Asistentes de IA:** Se utilizaron modelos de lenguaje (LLMs) como herramientas de aceleración y pair-programming para scaffolding de código, generación de pruebas unitarias exhaustivas y asistencia en redacción documental. Todo el código resultante ha sido auditado, probado y es enteramente explicable y modificable por el autor en la defensa oral y modificación en vivo.

---

## 13. Licencia

Este proyecto está distribuido bajo la licencia **MIT**. Consulte el archivo [LICENSE](LICENSE) para obtener más detalles.
