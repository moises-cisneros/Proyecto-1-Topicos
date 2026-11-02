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

## 3. Pipeline de Procesamiento de Lenguaje Natural (NLP)

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
(4) Normalización Morfológica (Stemming vs. Lematización)
    └── SnowballStemmer (baja latencia) vs. SpaCy es_core_news_sm (densidad léxica)
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

## 4. Modelos de Machine Learning y Evaluación

El sistema implementa y compara de forma empírica tres aproximaciones:

| Modelo | Rol | Justificación Técnica |
| :--- | :--- | :--- |
| **DummyClassifier** | Línea Base (*Baseline*) | Estrategia de clase mayoritaria (`most_frequent`) para medir el valor agregado real del modelado. |
| **Multinomial Naive Bayes** | Modelo Principal | Alta efectividad con representaciones dispersas TF-IDF, baja latencia y robustez en textos breves. Alisado de Laplace $\alpha$. |
| **Regresión Logística** | Modelo Desafiante | Frontera de decisión lineal calibrada, interpretabilidad directa de coeficientes e hiperparámetro de regularización $C$. |

### Protocolo de Evaluación

- **Partición:** División estratificada 80/20 (`random_state=42`) manteniendo proporción `ham`/`spam`.
- **Validación Cruzada:** 5-Fold Stratified K-Fold sobre el conjunto de entrenamiento para la sintonía de hiperparámetros.
- **Métricas:** Matriz de Confusión, Precisión, Exhaustividad (Recall), F1-Score (clase spam y macro) y Tasa de Falsos Positivos (para prevenir el bloqueo de mensajes legítimos).
- **Diagnóstico de Errores:** Análisis cualitativo sistemático de Falsos Positivos y Falsos Negativos para identificar casos de borde y vocabulario no observado.

---

## 5. Referencia de Endpoints API

La API REST expone los siguientes puntos de entrada documentados:

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `POST` | `/predict` | Clasifica un mensaje SMS individual, retornando etiqueta, probabilidad y nivel de riesgo. |
| `POST` | `/predict/batch` | Clasifica lotes de mensajes o archivos estructurados (CSV). |
| `POST` | `/nlp/debug` | Retorna el desglose paso a paso de las transformaciones de NLP para explicabilidad. |
| `GET` | `/metrics` | Retorna las métricas comparativas de los modelos evaluados en el conjunto de prueba. |
| `GET` | `/history` | Consulta el registro histórico de clasificaciones persistidas en PostgreSQL. |
| `GET` | `/health` | Chequeo de estado del servicio, estado de la base de datos y versión del pipeline. |

---

## 6. Estructura del Repositorio

```
SMS-Sentinel/
├── api/                       # Servicio REST FastAPI
│   ├── routes/                # Controladores de endpoints (/predict, /metrics, etc.)
│   ├── schemas/               # Modelos Pydantic v2 de entrada y salida
│   ├── database/              # Conexión SQLAlchemy y modelos ORM
│   └── main.py                # Punto de entrada de la aplicación API
├── src/                       # Núcleo de NLP y Machine Learning
│   ├── nlp/                   # Preprocesadores, regex, stopwords y tokenizadores
│   │   ├── normalizer.py      # Enmascaramiento de entidades y regex
│   │   ├── tokenizer.py       # Segmentación y limpieza de tokens
│   │   └── pipeline_builder.py# Ensamblador de Pipeline de scikit-learn
│   └── models/                # Entrenamiento, evaluación y serialización
│       ├── train.py           # Script unificado y reproducible de entrenamiento
│       └── evaluate.py        # Generación de métricas y análisis de errores
├── web/                       # Aplicación Frontend en React + TypeScript
│   ├── src/components/        # Componentes UI (Inspector NLP, Métricas, Predictor)
│   └── src/services/          # Clientes API HTTP
├── notebooks/                 # Experimentación reproducible
│   ├── 01_eda.ipynb           # Análisis exploratorio de datos y distribuciones
│   ├── 02_nlp_experiments.ipynb # Benchmarks: Stemming vs Lematización, N-gramas
│   └── 03_model_training.ipynb# Ajuste de hiperparámetros y matriz de confusión
├── data/                      # Almacenamiento local de datos (ignorado en git)
│   ├── raw/                   # Conjuntos de datos originales
│   └── processed/             # Particiones procesadas
├── models/                    # Artefactos serializados (.joblib)
├── docker/                    # Dockerfiles y configuraciones de servicios
├── docker-compose.yml         # Orquestación de contenedores (Frontend, API, DB)
├── scripts/                   # Utilidades de desarrollo y verificación
├── LICENSE                    # Licencia MIT
└── README.md                  # Documentación principal
```

---

## 7. Puesta en Marcha (Quickstart)

### Opción A: Despliegue con Docker Compose (Recomendado)

Inicia todos los servicios con puertos mapeados y aislados:

```bash
docker compose up --build
```

- **Frontend Web:** [http://localhost:3090](http://localhost:3090)
- **API Swagger UI:** [http://localhost:8090/docs](http://localhost:8090/docs)
- **PostgreSQL:** `localhost:5439`

### Opción B: Ejecución Local para Desarrollo

#### 1. Entorno Backend y Machine Learning

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Instalar dependencias
pip install -r api/requirements.txt

# Descargar recursos de NLP
python -m spacy download es_core_news_sm
python -c "import nltk; nltk.download('stopwords'); nltk.download('punkt')"

# Entrenar pipeline completo
python src/models/train.py

# Iniciar servidor FastAPI
uvicorn api.main:app --host 0.0.0.0 --port 8090 --reload
```

#### 2. Entorno Frontend

```bash
cd web
pnpm install
pnpm dev --port 3090
```

---

## 8. Calidad de Código y Estándares de Contribución

- **Commits Convencionales:** Se adhiere al estándar [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`).
- **Pipeline Determinista:** Semillas fijadas a `random_state=42` en todas las etapas estocásticas.
- **Validación Automática:** Scripts de validación previa disponibles en `scripts/pre_commit_check.ps1`.

---

## 9. Licencia

Este proyecto está distribuido bajo la licencia **MIT**. Consulte el archivo [LICENSE](LICENSE) para obtener más detalles.
