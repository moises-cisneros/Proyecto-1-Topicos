"""SMS Sentinel - Microservicio REST API con FastAPI.

Expone endpoints para:
- Estado de salud y diagnóstico (GET /health)
- Documentación interactiva Swagger/OpenAPI (GET /docs)
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.schemas import HealthResponse


# Rutas de artefactos por defecto o configuradas vía variables de entorno
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: inicialización de recursos."""
    model_file = resolve_path(DEFAULT_MODEL_PATH)
    app.state.pipeline = None
    app.state.model_name = "None"

    if model_file.exists():
        try:
            import joblib
            from src.nlp.pipeline_builder import preprocess_for_pipeline  # noqa: F401
            app.state.pipeline = joblib.load(model_file)
            classifier = app.state.pipeline.named_steps.get("classifier")
            app.state.model_name = classifier.__class__.__name__ if classifier else "UnknownClassifier"
        except Exception:
            app.state.pipeline = None
            app.state.model_name = "ErrorLoadingModel"

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
