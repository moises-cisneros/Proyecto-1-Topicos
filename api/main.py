"""SMS Sentinel - Microservicio REST API con FastAPI.

Expone endpoints para:
- Inferencia individual (POST /predict)
- Inferencia por lotes (POST /predict/batch y POST /predict/batch/csv)
- Consulta de métricas del modelo (GET /metrics)
- Estado de salud y diagnóstico (GET /health)
- Documentación interactiva Swagger/OpenAPI (GET /docs)
"""

import io
import json
import os
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from sklearn.pipeline import Pipeline

from api.schemas import (
    BatchInput,
    BatchResponse,
    BatchSummary,
    HealthResponse,
    MessageInput,
    MetricsResponse,
    PredictionResponse,
)
from src.nlp.normalizer import normalize_text
# Importar preprocess_for_pipeline para deserialización correcta de joblib
from src.nlp.pipeline_builder import preprocess_for_pipeline  # noqa: F401


# Rutas de artefactos por defecto o configuradas vía variables de entorno
DEFAULT_MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/spam_detector_pipeline.joblib"))
DEFAULT_METRICS_PATH = Path(os.getenv("METRICS_PATH", "models/metrics.json"))


def resolve_path(target_path: Path) -> Path:
    """Resuelve la ruta absoluta de un archivo buscando desde cwd o raíz del proyecto."""
    if target_path.is_absolute() and target_path.exists():
        return target_path
    
    # 1. Probar ruta directa desde cwd
    if target_path.exists():
        return target_path.resolve()
        
    # 2. Probar relativo al directorio padre de api/ (raíz del proyecto)
    project_root = Path(__file__).resolve().parent.parent
    candidate = project_root / target_path
    if candidate.exists():
        return candidate.resolve()

    return target_path.resolve()


def compute_risk_level(spam_probability: float) -> str:
    """Calcula el nivel de riesgo semántico a partir de la probabilidad de spam."""
    if spam_probability >= 0.70:
        return "CRÍTICO"
    elif spam_probability >= 0.35:
        return "MEDIO"
    return "BAJO"


def extract_detected_tokens(raw_text: str) -> list[str]:
    """Extrae los tokens sintéticos detectados durante la normalización."""
    normalized = normalize_text(raw_text)
    return list(dict.fromkeys(re.findall(r"TOKEN_[A-Z]+", normalized)))


def run_single_inference(pipeline: Pipeline, text: str) -> PredictionResponse:
    """Ejecuta la inferencia sobre una cadena de texto y retorna PredictionResponse."""
    t0 = time.perf_counter()
    
    prediction = pipeline.predict([text])[0]
    probabilities = pipeline.predict_proba([text])[0]
    classes = list(pipeline.classes_)
    
    spam_idx = classes.index("spam")
    ham_idx = classes.index("ham")
    
    prob_spam = float(probabilities[spam_idx])
    prob_ham = float(probabilities[ham_idx])
    
    risk_level = compute_risk_level(prob_spam)
    detected_tokens = extract_detected_tokens(text)
    latency_ms = round((time.perf_counter() - t0) * 1000, 3)

    return PredictionResponse(
        label=str(prediction),
        spam_probability=round(prob_spam, 4),
        ham_probability=round(prob_ham, 4),
        risk_level=risk_level,
        latency_ms=latency_ms,
        detected_tokens=detected_tokens,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: carga artefactos en memoria al iniciar."""
    model_file = resolve_path(DEFAULT_MODEL_PATH)
    metrics_file = resolve_path(DEFAULT_METRICS_PATH)
    
    # 1. Cargar pipeline entrenado
    if model_file.exists():
        try:
            app.state.pipeline = joblib.load(model_file)
            classifier = app.state.pipeline.named_steps.get("classifier")
            app.state.model_name = classifier.__class__.__name__ if classifier else "UnknownClassifier"
        except Exception:
            app.state.pipeline = None
            app.state.model_name = "ErrorLoadingModel"
    else:
        app.state.pipeline = None
        app.state.model_name = "ModelNotFound"

    # 2. Cargar métricas de evaluación
    if metrics_file.exists():
        try:
            with open(metrics_file, "r", encoding="utf-8") as f:
                app.state.metrics = json.load(f)
        except Exception:
            app.state.metrics = None
    else:
        app.state.metrics = None

    yield
    
    # Limpieza al apagar la aplicación
    app.state.pipeline = None
    app.state.metrics = None


app = FastAPI(
    title="SMS Sentinel API",
    description=(
        "Microservicio REST de alta velocidad para detección de Spam y Phishing en SMS "
        "en español utilizando NLP y Machine Learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS para integración con Frontend (puerto 3090)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Ruta raíz de bienvenida")
async def root():
    """Ruta raíz que confirma la ejecución del servicio y enlaza a la documentación."""
    return {
        "service": "SMS Sentinel API",
        "status": "UP",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/health",
        "metrics_url": "/metrics",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    summary="Verificar estado de salud y disponibilidad del modelo",
)
async def health_check():
    """Retorna el estado de operatividad de la API, modelo cargado y marca de tiempo."""
    pipeline_loaded = getattr(app.state, "pipeline", None) is not None
    model_name = getattr(app.state, "model_name", "None")
    current_status = "UP" if pipeline_loaded else "DEGRADED"

    return HealthResponse(
        status=current_status,
        model_loaded=pipeline_loaded,
        model_name=model_name,
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post(
    "/predict",
    response_model=PredictionResponse,
    summary="Clasificar un mensaje SMS individual",
    status_code=status.HTTP_200_OK,
)
async def predict_single(message: MessageInput):
    """Clasifica un mensaje SMS individual devolviendo etiqueta, probabilidades y riesgo."""
    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo de clasificación de SMS no está disponible en memoria.",
        )

    return run_single_inference(pipeline, message.text)


@app.post(
    "/predict/batch",
    response_model=BatchResponse,
    summary="Clasificar un lote de mensajes SMS vía JSON",
    status_code=status.HTTP_200_OK,
)
async def predict_batch_json(batch: BatchInput):
    """Clasifica una colección de mensajes SMS enviados en formato JSON."""
    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo de clasificación de SMS no está disponible en memoria.",
        )

    t_start = time.perf_counter()
    predictions: list[PredictionResponse] = []
    spam_count = 0
    ham_count = 0

    for msg in batch.messages:
        pred = run_single_inference(pipeline, msg.text)
        predictions.append(pred)
        if pred.label == "spam":
            spam_count += 1
        else:
            ham_count += 1

    total = len(predictions)
    total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
    avg_latency = round(total_latency_ms / total, 3) if total > 0 else 0.0
    spam_pct = round((spam_count / total) * 100, 2) if total > 0 else 0.0

    return BatchResponse(
        summary=BatchSummary(
            total=total,
            spam_count=spam_count,
            ham_count=ham_count,
            spam_percentage=spam_pct,
            avg_latency_ms=avg_latency,
        ),
        total_latency_ms=total_latency_ms,
        predictions=predictions,
    )


@app.post(
    "/predict/batch/csv",
    response_model=BatchResponse,
    summary="Clasificar un lote de mensajes SMS vía archivo CSV",
    status_code=status.HTTP_200_OK,
)
async def predict_batch_csv(file: UploadFile = File(...)):
    """Procesa y clasifica un archivo CSV que contiene mensajes SMS."""
    pipeline = getattr(app.state, "pipeline", None)
    if pipeline is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El modelo de clasificación de SMS no está disponible en memoria.",
        )

    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo proporcionado debe tener extensión .csv",
        )

    content = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(content))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Error al analizar el archivo CSV: {str(exc)}",
        )

    # Identificar columna con texto
    target_col = None
    for candidate in ["text", "text_es", "sms", "mensaje", "content"]:
        if candidate in df.columns:
            target_col = candidate
            break

    if target_col is None:
        if len(df.columns) > 0:
            target_col = df.columns[0]
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El archivo CSV no contiene columnas válidas.",
            )

    texts = df[target_col].dropna().astype(str).tolist()
    if not texts:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El archivo CSV no contiene registros de texto no nulos.",
        )

    if len(texts) > 1000:
        texts = texts[:1000]

    t_start = time.perf_counter()
    predictions: list[PredictionResponse] = []
    spam_count = 0
    ham_count = 0

    for text in texts:
        clean_text = text.strip()
        if not clean_text:
            continue
        pred = run_single_inference(pipeline, clean_text)
        predictions.append(pred)
        if pred.label == "spam":
            spam_count += 1
        else:
            ham_count += 1

    total = len(predictions)
    if total == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Ningún registro del archivo CSV contiene texto procesable.",
        )

    total_latency_ms = round((time.perf_counter() - t_start) * 1000, 2)
    avg_latency = round(total_latency_ms / total, 3) if total > 0 else 0.0
    spam_pct = round((spam_count / total) * 100, 2) if total > 0 else 0.0

    return BatchResponse(
        summary=BatchSummary(
            total=total,
            spam_count=spam_count,
            ham_count=ham_count,
            spam_percentage=spam_pct,
            avg_latency_ms=avg_latency,
        ),
        total_latency_ms=total_latency_ms,
        predictions=predictions,
    )


@app.get(
    "/metrics",
    summary="Consultar métricas de evaluación del modelo en producción",
)
async def get_metrics():
    """Retorna las métricas cuantitativas y cualitativas de evaluación del modelo."""
    metrics = getattr(app.state, "metrics", None)
    if metrics is None:
        # Intentar cargar en caliente si no estaba al arrancar
        metrics_file = resolve_path(DEFAULT_METRICS_PATH)
        if metrics_file.exists():
            with open(metrics_file, "r", encoding="utf-8") as f:
                metrics = json.load(f)
                app.state.metrics = metrics

    if metrics is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El archivo de métricas de evaluación no está disponible.",
        )

    return metrics
