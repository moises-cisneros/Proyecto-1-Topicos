"""Paquete unificado de Procesamiento de Lenguaje Natural (NLP) y Machine Learning para SMS Sentinel.

Estructura del paquete:
- pipeline.nlp: Normalización regex, enmascaramiento de tokens sintéticos, stopwords contextualizadas y lematización/stemming.
- pipeline.models: Entrenamiento determinista, validación cruzada estratificada, benchmarking y serialización joblib.
"""

from pipeline.nlp import (
    DEFAULT_WHITELIST,
    NEGATION_WHITELIST,
    SYNTHETIC_TOKENS,
    TOKEN_NUM,
    TOKEN_TEL,
    TOKEN_URL,
    URGENCY_WHITELIST,
    build_sms_pipeline,
    explain_text,
    filter_stopwords,
    get_spanish_stopwords,
    inspect_nlp_pipeline,
    inspect_pipeline_prediction,
    lemmatize_tokens,
    mask_entities,
    normalize_text,
    preprocess_for_pipeline,
    preprocess_for_pipeline_lemmatized,
    preprocess_for_pipeline_raw,
    preprocess_for_pipeline_stemmed,
    preprocess_text,
    stem_tokens,
    tokenize_text,
)
from pipeline.models import (
    evaluate_model,
    format_metrics_table,
    perform_qualitative_error_analysis,
    train_and_evaluate,
)

__version__ = "1.0.0"

__all__ = [
    "TOKEN_URL",
    "TOKEN_TEL",
    "TOKEN_NUM",
    "SYNTHETIC_TOKENS",
    "mask_entities",
    "normalize_text",
    "NEGATION_WHITELIST",
    "URGENCY_WHITELIST",
    "DEFAULT_WHITELIST",
    "get_spanish_stopwords",
    "filter_stopwords",
    "tokenize_text",
    "stem_tokens",
    "lemmatize_tokens",
    "preprocess_text",
    "inspect_nlp_pipeline",
    "preprocess_for_pipeline",
    "preprocess_for_pipeline_stemmed",
    "preprocess_for_pipeline_lemmatized",
    "preprocess_for_pipeline_raw",
    "build_sms_pipeline",
    "inspect_pipeline_prediction",
    "explain_text",
    "evaluate_model",
    "format_metrics_table",
    "perform_qualitative_error_analysis",
    "train_and_evaluate",
]
