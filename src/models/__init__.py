"""Módulo de Modelado de Machine Learning, Evaluación y Benchmarking para SMS Sentinel."""

from src.models.evaluate import (
    evaluate_model,
    format_metrics_table,
    perform_qualitative_error_analysis,
)
from src.models.train import train_and_evaluate

__all__ = [
    "train_and_evaluate",
    "evaluate_model",
    "perform_qualitative_error_analysis",
    "format_metrics_table",
]

