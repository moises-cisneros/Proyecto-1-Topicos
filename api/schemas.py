"""Esquemas de validación y transferencia de datos (Pydantic v2) para SMS Sentinel API.

Define contratos estrictos de entrada y salida para inferencia individual,
procesamiento por lotes, métricas, auditoría de base de datos y estado de salud del servicio.
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageInput(BaseModel):
    """Esquema de entrada para clasificación de un mensaje SMS individual."""
    
    text: str = Field(
        ...,
        description="Texto del mensaje SMS a clasificar (longitud entre 1 y 1000 caracteres)",
        min_length=1,
        max_length=1000,
        examples=["URGENTE: Su cuenta ha sido bloqueada. Ingrese a http://banco-alerta.com"]
    )

    @field_validator("text")
    @classmethod
    def validate_not_whitespace(cls, v: str) -> str:
        """Rechaza textos vacíos o conformados exclusivamente por espacios en blanco."""
        stripped = v.strip()
        if not stripped:
            raise ValueError(
                "El texto del mensaje no puede estar vacío ni contener únicamente espacios en blanco."
            )
        return stripped

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "text": "AVISO BANCO: Su tarjeta ha sido bloqueada. Acceda a http://banco-seguro.es para reactivarla."
            }
        }
    )


class PredictionResponse(BaseModel):
    """Esquema de respuesta para la clasificación de un mensaje SMS."""

    label: str = Field(
        ...,
        description="Etiqueta predicha por el modelo supervisado ('ham' o 'spam')",
        examples=["spam"]
    )
    spam_probability: float = Field(
        ...,
        description="Probabilidad calibrada de que el mensaje sea spam (0.0 a 1.0)",
        examples=[0.9782]
    )
    ham_probability: float = Field(
        ...,
        description="Probabilidad calibrada de que el mensaje sea legítimo (0.0 a 1.0)",
        examples=[0.0218]
    )
    risk_level: str = Field(
        ...,
        description="Nivel semántico de riesgo ('BAJO', 'MEDIO', 'CRÍTICO')",
        examples=["CRÍTICO"]
    )
    latency_ms: float = Field(
        ...,
        description="Tiempo de inferencia del procesamiento en milisegundos",
        examples=[3.42]
    )
    detected_tokens: list[str] = Field(
        default_factory=list,
        description="Tokens sintéticos o palabras clave detectadas durante la normalización",
        examples=[["TOKEN_URL", "TOKEN_TEL"]]
    )
    text: Optional[str] = Field(
        default=None,
        description="Texto original del mensaje evaluado (incluido en lote)",
        examples=["URGENTE: Ingrese a http://banco.com"]
    )


class BatchInput(BaseModel):
    """Esquema de entrada para clasificación masiva por lotes vía JSON."""

    messages: list[MessageInput] = Field(
        ...,
        description="Lista de mensajes SMS a procesar (entre 1 y 500 mensajes)",
        min_length=1,
        max_length=500
    )


class BatchSummary(BaseModel):
    """Estadísticas resumidas del lote procesado."""

    total: int = Field(..., description="Total de mensajes evaluados en el lote")
    spam_count: int = Field(..., description="Cantidad de mensajes clasificados como spam")
    ham_count: int = Field(..., description="Cantidad de mensajes clasificados como ham")
    spam_percentage: float = Field(..., description="Porcentaje de spam en el lote (0.0 a 100.0)")
    avg_latency_ms: float = Field(..., description="Latencia promedio por mensaje en milisegundos")


class BatchResponse(BaseModel):
    """Esquema de respuesta para el procesamiento por lotes."""

    summary: BatchSummary
    total_latency_ms: float = Field(..., description="Tiempo total de inferencia del lote en milisegundos")
    predictions: list[PredictionResponse] = Field(..., description="Resultados detallados por cada mensaje")


class HealthResponse(BaseModel):
    """Esquema de respuesta del estado de salud y operatividad de la API."""

    status: str = Field("UP", description="Estado operativo del servicio ('UP', 'DEGRADED', 'DOWN')")
    model_loaded: bool = Field(..., description="Indica si el pipeline .joblib está cargado en memoria")
    model_name: str = Field(..., description="Nombre del modelo clasificador en producción")
    version: str = Field("1.0.0", description="Versión de la API")
    timestamp: str = Field(..., description="Marca de tiempo ISO-8601 del servidor")
    database_connected: bool = Field(False, description="Indica si la base de datos de auditoría está conectada")


class MetricsResponse(BaseModel):
    """Esquema de respuesta de las métricas históricas de evaluación del modelo."""

    timestamp: str = Field(..., description="Fecha y hora de generación de las métricas")
    winner_model: str = Field(..., description="Nombre del modelo ganador en producción")
    hyperparameter_tuning: dict[str, Any] = Field(..., description="Resultados de búsqueda de hiperparámetros")
    benchmark_summary: list[dict[str, Any]] = Field(..., description="Comparativa de modelos evaluados")


class MessageAuditRecord(BaseModel):
    """Esquema de un registro individual en la auditoría de mensajes persistidos."""

    id: int = Field(..., description="Identificador único autoincremental de la auditoría")
    created_at: datetime = Field(..., description="Marca de tiempo UTC en la que se evaluó el mensaje")
    message_text: str = Field(..., description="Texto original del mensaje evaluado")
    prediction: str = Field(..., description="Etiqueta predicha ('ham' o 'spam')")
    probability_spam: float = Field(..., description="Probabilidad calibrada de spam")
    probability_ham: float = Field(..., description="Probabilidad calibrada de ham")
    risk_level: str = Field(..., description="Nivel semántico de riesgo ('BAJO', 'MEDIO', 'CRÍTICO')")
    detected_tokens: list[str] = Field(default_factory=list, description="Tokens sintéticos detectados")
    latency_ms: float = Field(..., description="Latencia de procesamiento en milisegundos")

    model_config = ConfigDict(from_attributes=True)


class HistoryResponse(BaseModel):
    """Esquema de respuesta paginada para el historial de auditoría de mensajes."""

    total: int = Field(..., description="Total de registros de auditoría persistidos en el sistema")
    limit: int = Field(..., description="Límite de registros solicitados por página")
    offset: int = Field(..., description="Desplazamiento aplicado a la consulta")
    records: list[MessageAuditRecord] = Field(..., description="Lista de registros de auditoría ordenados por fecha descendente")


class TFIDFFeatureWeight(BaseModel):
    """Ponderación numérica de un término o n-grama extraído en el vector TF-IDF."""

    feature: str = Field(
        ...,
        description="Palabra, token sintético o n-grama extraído por TF-IDF",
        examples=["TOKEN_URL"],
    )
    weight: float = Field(
        ...,
        description="Peso numérico calculado por TfidfVectorizer con sublinear_tf",
        examples=[0.5842],
    )


class NLPDebugResponse(BaseModel):
    """Esquema de respuesta para la depuración y explicabilidad paso a paso de NLP."""

    original: str = Field(
        ...,
        description="Texto original recibido sin procesar",
        examples=["URGENTE: Su cuenta ha sido bloqueada. Ingrese a http://banco-alerta.com"],
    )
    normalized: str = Field(
        ...,
        description="Texto resultante tras normalización de tildes y enmascaramiento regex de entidades",
        examples=["urgente su cuenta ha sido bloqueada ingrese a TOKEN_URL"],
    )
    tokens: list[str] = Field(
        ...,
        description="Unidades léxicas tokenizadas respetando fronteras y tokens sintéticos intactos",
        examples=[["urgente", "su", "cuenta", "ha", "sido", "bloqueada", "ingrese", "a", "TOKEN_URL"]],
    )
    no_stopwords: list[str] = Field(
        ...,
        description="Tokens depurados tras filtrado de stop words preservando la whitelist contextual",
        examples=[["urgente", "cuenta", "bloqueada", "ingrese", "TOKEN_URL"]],
    )
    stemmed_or_lemmatized: list[str] = Field(
        ...,
        description="Tokens tras reducción morfológica (Snowball stemming) sin recortar tokens sintéticos",
        examples=[["urgent", "cuent", "bloque", "ingres", "TOKEN_URL"]],
    )
    tfidf_top_features: list[TFIDFFeatureWeight] = Field(
        default_factory=list,
        description="Lista de las palabras o n-gramas con mayor peso TF-IDF en el mensaje",
    )

