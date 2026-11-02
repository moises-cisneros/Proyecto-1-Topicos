# Informe Técnico: SMS Sentinel

## Detección de Spam y Phishing en SMS mediante NLP y Machine Learning

> **Sistema:** SMS Sentinel — Security Operations & Threat Gateway  
> **Autor:** Moises Cisneros (`moisescisnerosdl@gmail.com`)  
> **Fecha:** Noviembre 2026  
> **Licencia:** MIT  

---

## 1. Definición del Problema y Justificación del Dominio

El fraude mediante mensajería móvil corta (SMS), comúnmente denominado **Smishing** o **SMS Phishing**, constituye uno de los vectores primarios de ingeniería social y suplantación de identidad en el sector financiero y de telecomunicaciones. A diferencia de las comunicaciones tradicionales de correo electrónico (que cuentan con cabeceras SPF, DKIM y DMARC), el protocolo SMS carece de autenticación nativa del remitente a nivel de usuario final, permitiendo que actores maliciosos disfracen alertas de transferencias no autorizadas, bloqueos de cuenta o entrega de paquetes para sustraer credenciales bancarias.

El objetivo de **SMS Sentinel** es construir una solución completa de ciberseguridad que opere como pasarela de inspección previa a la entrega. El sistema ingesta mensajes en español, aplica un pipeline determinista de Procesamiento de Lenguaje Natural (NLP), ejecuta inferencia en memoria en menos de 5 milisegundos mediante un clasificador supervisado de Machine Learning, persiste cada transacción de auditoría de forma inmutable en PostgreSQL y ofrece una interfaz web profesional con capacidad de análisis individual, ingesta masiva de archivos CSV y calibración de umbrales de decisión en vivo.

---

## 2. Dataset y Análisis Exploratorio de Datos (EDA)

### 2.1 Origen, Licencia y Protocolo de Preparación

* **Repositorio Fuente:** [`dbarbedillo/SMS_Spam_Multilingual_Collection_Dataset`](https://huggingface.co/datasets/dbarbedillo/SMS_Spam_Multilingual_Collection_Dataset) alojado en Hugging Face.
* **Origen Académico:** Derivado y traducido al español a partir del corpus canónico de referencia internacional *SMS Spam Collection Dataset*, compilado originalmente por Tiago A. Almeida y José María Gómez Hidalgo en el [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/228/sms+spam+collection) (2012).
* **Licencia:** Abierta para investigación académica y desarrollo tecnológico (CC BY 4.0 / Public Domain).
* **Volumen Total:** 5.572 registros etiquetados en español sin valores nulos ni duplicados residuales.
* **Distribución de Clases:**
  * **Comunicaciones Legítimas (`ham`):** 4.827 registros (86.63%)
  * **Comunicaciones Maliciosas (`spam`):** 745 registros (13.37%)
* **Protocolo de Preparación y Limpieza:**
  1. **Extracción Lingüística:** Se filtró el corpus multilingüe extrayendo exclusivamente la columna `text_es` como campo de texto objetivo (`text`) y la etiqueta binaria normalizada (`label`: `ham` / `spam`).
  2. **Auditoría de Integridad:** Se verificó la ausencia total de celdas nulas o registros vacíos, normalizando espacios en blanco periféricos y almacenando el archivo crudo en `data/raw/sms_spanish.csv`.
  3. **Partición Estratificada Fija (80/20):** Mediante el script determinista `scripts/prepare_data.py` (ejecutable vía `pnpm data:prepare`), se aplicó una partición estratificada con semilla pseudoaleatoria fija (`random_state=42`) para garantizar la preservación exacta de las proporciones en ambas particiones:
     * **Conjunto de Entrenamiento (`data/processed/train.csv`):** 4.457 registros (3.861 ham [86.63%], 596 spam [13.37%]).
     * **Conjunto de Evaluación Holdout (`data/processed/test.csv`):** 1.115 registros (966 ham [86.64%], 149 spam [13.36%]).
  4. **Aislamiento Estricto (No Data Leakage):** El conjunto de prueba `test.csv` quedó estrictamente congelado y jamás fue consultado para sintonizar hiperparámetros, extraer frecuencias o calcular estadísticas TF-IDF, utilizándose exclusivamente para el benchmarking final.

### 2.2 Hallazgos del EDA y Justificación de Preprocesamiento

1. **Longitud de Texto:** Los mensajes de spam presentan una longitud media significativamente mayor (145.2 caracteres frente a 72.8 caracteres en ham), aproximándose al límite técnico de un segmento SMS estándar (160 caracteres).
2. **Presencia de Entidades Específicas:** El 82.4% de los mensajes de spam contienen URLs acortadas o números telefónicos de tarificación especial/llamadas directas, mientras que en ham dicha presencia es inferior al 1.8%.
3. **Implicación Arquitectónica:** Borrar números y enlaces eliminaría los predictores con mayor ganancia de información (*information gain*). Por ello, se diseñó una estrategia de enmascaramiento por **tokens sintéticos**.

---

## 3. Pipeline de Preprocesamiento de Lenguaje Natural (NLP)

El sistema adhiere al **Principio de Pipeline Único**: las transformaciones de preprocesamiento se encuentran encapsuladas estrictamente dentro de un `sklearn.pipeline.Pipeline` serializado atómicamente en formato `.joblib`. El backend FastAPI jamás reimplementa transformaciones manuales en producción.

```
Texto Crudo (SMS)
       │
       ▼
[Fase 1: Normalización & Regex Tokens] ──► minúsculas, sin tildes, TOKEN_URL, TOKEN_TEL, TOKEN_NUM
       │
       ▼
[Fase 2: Tokenización Boundary-Safe]  ──► segmentación con fronteras léxicas (\b)
       │
       ▼
[Fase 3: Stop Words con Whitelist]     ──► remoción de conectores, preservación de urgencia ("no", "urgente", "ya")
       │
       ▼
[Fase 4: Reducción Morfológica]       ──► Snowball Stemming para español (latencia 15x inferior a spaCy)
       │
       ▼
[Fase 5: Vectorización TF-IDF]        ──► sublinear_tf=True, n-gramas (1, 2), max_features=5000, min_df=2
```

### 3.1 Fases Secuenciales de Transformación

1. **Normalización y Enmascaramiento Regex:**
   * Sustitución de hipervínculos `http[s]?://...` por `TOKEN_URL`.
   * Sustitución de números telefónicos de 7 o más dígitos por `TOKEN_TEL`.
   * Sustitución de montos monetarios o secuencias numéricas aisladas por `TOKEN_NUM`.
   * Eliminación de diacríticos y conversión a minúsculas para unificar variantes léxicas.
2. **Tokenización Boundary-Safe:**
   * Segmentación mediante expresión regular con fronteras de palabra (`\b`), garantizando que los tokens sintéticos no se fragmenten por los guiones bajos internos.
3. **Stop Words con Whitelist Contextual:**
   * Se utiliza el catálogo base de stop words en español, filtrando determinantes y preposiciones vacías.
   * **Whitelist Contextual:** Se prohíbe la eliminación de palabras de polaridad negativa (`no`, `sin`, `ni`) y términos críticos de urgencia bancaria (`urgente`, `bloqueada`, `alerta`, `cuenta`, `aviso`, `seguridad`, `clave`).
4. **Motor Morfológico Dual: Stemming vs. Lematización (Evaluación Empírica):**
   * El pipeline implementa soporte modular nativo para ambas técnicas (`morphology="stemming" | "lemmatization"`):
     * **Snowball Stemming:** Reducción algorítmica de sufijos para español. Extremadamente veloz (< 0.1 ms/mensaje) y base del pipeline en producción.
     * **Lematización Canónica en Español:** Reducción flexiva de formas verbales y plurales al lema léxico de diccionario (`bloqueada` -> `bloquear`, `cuentas` -> `cuenta`), preservando intactos los tokens sintéticos.
   * **Benchmarking comparativo:** En `notebooks/02_nlp_experiments.ipynb` se evaluó el desempeño entre ambas técnicas. Ambas alcanzan puntuaciones prácticamente idénticas (F1-Macro: 0.9709 con Stemming vs 0.9724 con Lematización; F1-Spam: 0.9495 vs 0.9521). Frente a librerías externas pesadas (como spaCy `es_core_news_sm` que añade una latencia de 48.7 ms por mensaje violando el SLA), la solución implementada opera en memoria en tiempo real, permitiendo alternar entre ambas con el flag `--morphology` de forma inmediata.
5. **Vectorización TF-IDF Sublineal:**
   * `sublinear_tf=True`: Escala la frecuencia de términos mediante $1 + \log(\text{tf})$, evitando que la repetición artificial de una palabra distorsione el vector.
   * `ngram_range=(1, 2)`: Captura combinaciones bi-gramáticas críticas como *"cuenta bloqueada"*, *"premio exclusivo"* o *"transferencia autorizada"*.
   * `max_features=5000` y `min_df=2`: Eliminación de palabras hapax (que aparecen una sola vez) reduciendo la dispersión innecesaria.

---

## 4. Modelado Predictivo y Benchmarking

Se evaluaron tres modelos bajo condiciones idénticas sobre el conjunto holdout de prueba (1.115 registros independientes) tras sintonización de hiperparámetros mediante **5-Fold Stratified Cross-Validation** sobre el conjunto de entrenamiento:

### 4.1 Resultados Comparativos en el Conjunto de Prueba

| Modelo | Hiperparámetros Óptimos | Accuracy | F1-Macro | Precision (Spam) | Recall (Spam) | F1-Score (Spam) | Latencia Media |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Dummy Most Frequent)** | Estrategia fija `most_frequent` | 86.64% | 0.4642 | 0.00% | 0.00% | 0.00% | 0.8 ms |
| **Multinomial Naive Bayes** | Suavizado Laplace $\alpha = 0.1$ | 98.21% | 0.9594 | **98.50%** | 87.92% | 0.9291 | 1.2 ms |
| **Logistic Regression (Ganador)** | Regularización $C = 50.0$, Solver `lbfgs` | **98.65%** | **0.9709** | 95.27% | **94.63%** | **0.9495** | 1.9 ms |

### 4.2 Matriz de Confusión del Modelo en Producción (Logistic Regression)

* **Verdaderos Negativos (TN):** 959 (mensajes benignos correctamente entregados).
* **Falsos Positivos (FP):** 7 (tasa de falso positivo $FPR = 0.72\%$).
* **Falsos Negativos (FN):** 8 (amenazas no detectadas, $FNR = 5.37\%$).
* **Verdaderos Positivos (TP):** 141 (ataques de smishing neutralizados).

### 4.3 Análisis Cualitativo de Errores (Diagnóstico de Causa Raíz)

1. **Falsos Positivos (FP):** Comunicaciones legítimas que utilizaron léxico típico de promociones comerciales agresivas (ej. *"Liquidación especial solo por hoy en sucursal central"*). Causa: coexistencia de bigramas de urgencia sin vector de URL maliciosa.
2. **Falsos Negativos (FN):** Mensajes de smishing sumamente cortos o con ofuscación intencional de enlaces mediante espacios en blanco o formatos no estándar que eludieron las regex de enmascaramiento.

---

## 5. Arquitectura del Sistema e Integración End-to-End

El software se diseñó bajo una arquitectura desacoplada hexagonal orquestada mediante Docker Compose y gobernada por un monorepo pnpm:

```
[Cliente Web: React 18 + Vite]  ──► Puerto 3090 (Nginx / Dev Server)
       │  (HTTP / JSON / CSV)
       ▼
[Backend: FastAPI REST API]      ──► Puerto 8090 (Uvicorn ASGI)
       │  (SQLAlchemy Pooling)
       ▼
[Persistencia: PostgreSQL 16]    ──► Puerto 5439 (Aislamiento de Colisión)
```

### 5.1 Especificación de Capas y Aislamiento de Red

* **Capa Web (Frontend):** React 18, TypeScript, Tailwind CSS (paleta canónica `#2b2d42`, `#8d99ae`, `#edf2f4`, `#ef233c`, `#4361ee`) y cero animaciones. Dispone de escáner individual, ingesta masiva por lotes CSV con exportación de reportes, simulador de sensibilidad de umbrales y visor forense de explicabilidad (XAI).
* **Capa API (Backend):** FastAPI con esquemas Pydantic v2. Endpoints:
  * `POST /predict`: Inferencia individual con persistencia de auditoría transaccional.
  * `POST /predict/batch/csv`: Ingesta masiva multipart/form-data con procesamiento paralelo de hasta 1.000 mensajes.
  * `POST /nlp/debug`: Trazabilidad forense de las 5 fases intermedias y pesos TF-IDF.
  * `GET /metrics`: Telemetría del benchmark y sintonización de hiperparámetros.
  * `GET /history`: Auditoría paginada inmutable.
  * `GET /health`: Diagnóstico de disponibilidad de memoria y base de datos.
* **Capa de Persistencia (Base de Datos):** PostgreSQL en puerto `5439` (para evitar colisiones con el puerto predeterminado 5432). Implementa degradación elegante: si la base de datos se interrumpe, la API continúa prediciendo en memoria sin interrumpir el servicio.

---

## 6. Protocolo de Ensayos y Reconfiguración en Vivo

Para la validación técnica en vivo y pruebas de sensibilidad operativa, el sistema incorpora scripts parametrizados validados en la suite de pruebas `tests/test_live_reconfiguration.py`:

1. **Sensibilidad Léxica:** Modificación de la whitelist de stop words en `packages/pipeline/nlp/stopwords_es.py` y verificación inmediata del cambio en la matriz de tokens.
2. **Sensibilidad de N-Gramas:** Alternancia entre unigramas `(1,1)` y unigramas + bigramas `(1,2)` recalculando la dimensionalidad del vocabulario.
3. **Swapping de Clasificadores:** Posibilidad de alternar el estimador activo entre Naive Bayes y Regresión Logística mediante `packages/pipeline/models/train.py --classifier multinomial_nb`.
4. **Reentrenamiento Ultrarrápido (`--fast`):** Reentrenamiento en menos de 15 segundos actualizando atómicamente el binario `.joblib` y `models/metrics.json`.
5. **Threshold Tuning en la Web:** Control interactivo en el frontend para deslizar el umbral de decisión entre 20% y 80%, simulando el comportamiento agresivo requerido por entidades bancarias.

---

## 7. Instrucciones de Despliegue y Ejecución

### 7.1 Requisitos Previos

* Python 3.10+
* Node.js 18+ y pnpm 9+
* Docker y Docker Compose (opcional para ejecución aislada)

### 7.2 Ejecución con Docker Compose

```bash
# Levantar el entorno completo (Web: 3090, API: 8090, PostgreSQL: 5439)
docker compose up --build -d

# Verificación de logs
docker compose logs -f
```

### 7.3 Ejecución en Desarrollo Local

```bash
# 1. Instalar dependencias de Python
python -m venv .venv
.venv/Scripts/activate
pip install -r packages/api/requirements.txt pytest scikit-learn pandas joblib

# 2. Entrenar y serializar el modelo ganador
python packages/pipeline/models/train.py

# 3. Iniciar API FastAPI en puerto 8090
pnpm api:dev

# 4. Iniciar Frontend React en puerto 3090
pnpm install
pnpm dev
```

---

## 8. Conclusiones

**SMS Sentinel** demuestra que un problema de ciberseguridad crítico puede resolverse de forma rigurosa combinando técnicas fundamentales de NLP con modelos lineales bien calibrados, logrando una precisión superior al 98.6% y una latencia inferior a 2 milisegundos. La separación estricta de responsabilidades, la reproducibilidad total del pipeline y la gobernanza de auditoría transaccional convierten al sistema en una solución directamente transferible a entornos de producción corporativa.

---

## 9. Declaración de Honestidad Académica y Asistencia de Inteligencia Artificial

Conforme a las pautas de evaluación y honestidad académica estipuladas en la Sección 10 de la consigna (*Proyecto_Integrador.md*):

* **Autoría del Proyecto:** La formulación del problema, la estrategia de partición estratificada 80/20, el diseño del pipeline único determinista, la selección empírica de modelos frente a los 8 modelos de la materia y el desarrollo e integración de los tres paquetes (`packages/api`, `packages/pipeline`, `packages/web`) fueron concebidos, implementados y defendidos por el autor humano (**Moises Cisneros**).
* **Asistencia de Asistentes de IA:** Se utilizaron modelos de lenguaje (LLMs) como asistentes de programación por pares (*pair-programming*) y aceleración para tareas de generación de plantillas de pruebas automatizadas (`pytest`), scaffolding de esquemas Pydantic v2 y formateo de documentación técnica.
* **Dominio y Explicabilidad:** Todo el código fuente, la lógica matemática de la función de coste logística, los algoritmos de tokenización y los contratos de la API han sido auditados, verificados con 75 pruebas unitarias automatizadas y son completamente explicables y modificables en vivo por el autor durante la defensa individual y la modificación en vivo asignada por el docente.
