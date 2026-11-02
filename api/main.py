"""SMS Sentinel - Microservicio REST API con FastAPI.

Expone endpoints para:
- Inferencia individual (POST /predict)
- Estado de salud y diagnóstico (GET /health)
- Documentación interactiva Swagger/OpenAPI (GET /docs)
"""

import os
import re
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sklearn.pipeline import Pipeline

from api.schemas import HealthResponse, MessageInput, PredictionResponse
from src.nlp.normalizer import normalize_text
# Importar preprocess_for_pipeline para deserialización correcta de joblib
from src.nlp.pipeline_builder import preprocess_for_pipeline  # noqa: F401


DEFAULT_MODEL_PATH = Path(os.getenv("MODEL_PATH", "models/spam_detector_pipeline.joblib"))


def resolve_path(target_path: Path) -> Path:
    """Resuelve la ruta absoluta de un archivo buscando desde cwd o raíz del proyecto."""
    if target_path.is_absolute() and target_path.exists():
        return target_path
    
    if target_path.exists():
        return target_path.resolve()
        
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
    """Ciclo de vida de la aplicación: carga el pipeline entrenado en memoria."""
    model_file = resolve_path(DEFAULT_MODEL_PATH)
    
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

    yield
    app.state.pipeline = None


app = FastAPI(
    title="SMS Sentinel API",
    description=(
        "Microservicio REST de alta velocidad para detección de Spam y Phishing en SMS "
        "en español utilizando NLP y Machine Learning."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Configuración de CORS
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
