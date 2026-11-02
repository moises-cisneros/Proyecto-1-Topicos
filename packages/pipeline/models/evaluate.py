"""Módulo de evaluación integral, métricas de clasificación y diagnóstico cualitativo de errores.

Implementa los estándares técnicos de benchmarking para SMS Sentinel:
- Matriz de confusión desglosada (TP, FP, TN, FN).
- Métricas por clase (ham y spam), con especial énfasis en la Tasa de Falsos Positivos (FPR).
- Métricas agregadas (Macro F1, Weighted F1, Accuracy).
- Análisis cualitativo programático de muestras mal clasificadas (FP y FN) con diagnóstico técnico.
"""

from typing import Any, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.pipeline import Pipeline


def evaluate_model(
    pipeline: Pipeline,
    X_test: pd.Series | list[str],
    y_test: pd.Series | list[str],
    model_name: str = "Model",
) -> dict[str, Any]:
    """Evalúa un pipeline entrenado sobre el conjunto de test holdout.
    
    Calcula matriz de confusión, métricas a nivel de clase y métricas agregadas.
    
    Retorna:
        Diccionario serializable con las métricas detalladas.
    """
    y_test_arr = np.array(y_test)
    y_pred = np.array(pipeline.predict(X_test))

    # Matriz de confusión asumiendo etiquetas ['ham', 'spam']
    # labels order: ['ham', 'spam'] -> TN: ham predicho ham, FP: ham predicho spam, FN: spam predicho ham, TP: spam predicho spam
    cm = confusion_matrix(y_test_arr, y_pred, labels=["ham", "spam"])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # Tasa de Falsos Positivos (FPR) = FP / (FP + TN)
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0

    # Métricas por clase
    precision_ham = float(precision_score(y_test_arr, y_pred, pos_label="ham", zero_division=0))
    recall_ham = float(recall_score(y_test_arr, y_pred, pos_label="ham", zero_division=0))
    f1_ham = float(f1_score(y_test_arr, y_pred, pos_label="ham", zero_division=0))

    precision_spam = float(precision_score(y_test_arr, y_pred, pos_label="spam", zero_division=0))
    recall_spam = float(recall_score(y_test_arr, y_pred, pos_label="spam", zero_division=0))
    f1_spam = float(f1_score(y_test_arr, y_pred, pos_label="spam", zero_division=0))

    # Métricas globales
    acc = float(accuracy_score(y_test_arr, y_pred))
    f1_macro = float(f1_score(y_test_arr, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_test_arr, y_pred, average="weighted", zero_division=0))

    return {
        "model_name": model_name,
        "confusion_matrix": {
            "tn": tn,
            "fp": fp,
            "fn": fn,
            "tp": tp,
            "matrix": cm.tolist(),
        },
        "rates": {
            "false_positive_rate": round(fpr, 5),
            "false_negative_rate": round(float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0, 5),
        },
        "class_metrics": {
            "ham": {
                "precision": round(precision_ham, 4),
                "recall": round(recall_ham, 4),
                "f1_score": round(f1_ham, 4),
                "support": tn + fp,
            },
            "spam": {
                "precision": round(precision_spam, 4),
                "recall": round(recall_spam, 4),
                "f1_score": round(f1_spam, 4),
                "support": tp + fn,
            },
        },
        "aggregate_metrics": {
            "accuracy": round(acc, 4),
            "f1_macro": round(f1_macro, 4),
            "f1_weighted": round(f1_weighted, 4),
        },
    }


def perform_qualitative_error_analysis(
    pipeline: Pipeline,
    X_test: pd.Series | list[str],
    y_test: pd.Series | list[str],
    max_samples: int = 5,
) -> dict[str, list[dict[str, Any]]]:
    """Extrae y diagnostica cualitativamente falsos positivos y falsos negativos.
    
    Analiza:
    - Falsos Positivos (legítimos clasificados como spam).
    - Falsos Negativos (spam/phishing clasificados como ham).
    
    Provee una categorización técnica de la causa probable.
    """
    X_list = list(X_test)
    y_list = list(y_test)
    y_pred = list(pipeline.predict(X_list))

    classifier = pipeline.named_steps.get("classifier")
    has_proba = hasattr(classifier, "predict_proba")
    probas = pipeline.predict_proba(X_list) if has_proba else None
    classes = list(pipeline.classes_) if has_proba else []

    false_positives: list[dict[str, Any]] = []
    false_negatives: list[dict[str, Any]] = []

    for idx, (text, true_lbl, pred_lbl) in enumerate(zip(X_list, y_list, y_pred)):
        prob_spam = 0.0
        if probas is not None and "spam" in classes:
            prob_spam = float(probas[idx][classes.index("spam")])

        if true_lbl == "ham" and pred_lbl == "spam":
            diagnosis = _diagnose_false_positive(text)
            false_positives.append({
                "sample_index": idx,
                "text": text,
                "true_label": true_lbl,
                "predicted_label": pred_lbl,
                "spam_probability": round(prob_spam, 4),
                "diagnosis": diagnosis,
            })
        elif true_lbl == "spam" and pred_lbl == "ham":
            diagnosis = _diagnose_false_negative(text)
            false_negatives.append({
                "sample_index": idx,
                "text": text,
                "true_label": true_lbl,
                "predicted_label": pred_lbl,
                "spam_probability": round(prob_spam, 4),
                "diagnosis": diagnosis,
            })

    return {
        "false_positives": false_positives[:max_samples],
        "false_negatives": false_negatives[:max_samples],
        "total_false_positives": len(false_positives),
        "total_false_negatives": len(false_negatives),
    }


def _diagnose_false_positive(text: str) -> str:
    """Diagnóstico heurístico para falsos positivos."""
    lower = text.lower()
    if any(k in lower for k in ["urgente", "premio", "cuenta", "aviso", "banco", "transferencia", "ahora"]):
        return "Presencia de términos de urgencia o financieros en contexto legítimo (ambigüedad léxica)."
    if any(k in lower for k in ["http", "www", ".com", ".es"]):
        return "Presencia de enlace URL o web compartida en comunicación personal legítima."
    if len(text.split()) < 4:
        return "Mensaje excesivamente breve con escasez de señal contextual (sparsity)."
    return "Léxico atípico que colisiona con la distribución frecuencial de términos de spam."


def _diagnose_false_negative(text: str) -> str:
    """Diagnóstico heurístico para falsos negativos."""
    lower = text.lower()
    if len(text.split()) < 5:
        return "Texto excesivamente conciso que evade filtros TF-IDF por baja densidad léxica."
    if any(k in lower for k in ["hola", "buenos dias", "estimado", "amigo"]):
        return "Fraseo deceptivo con fórmulas de cortesía que enmascaran el vector de phishing."
    if any(c.isdigit() for c in text):
        return "Cargas útiles numéricas o códigos únicos sin términos léxicos explícitos de spam."
    return "Vocabulario de spam sutil o modismos no capturados en el vocabulario entrenado."


def format_metrics_table(evaluation_results: list[dict[str, Any]]) -> pd.DataFrame:
    """Genera una tabla comparativa a partir de múltiples resultados de evaluación."""
    rows = []
    for res in evaluation_results:
        cm = res["confusion_matrix"]
        cm_str = f"TN:{cm['tn']} FP:{cm['fp']} FN:{cm['fn']} TP:{cm['tp']}"
        rows.append({
            "Modelo": res["model_name"],
            "Accuracy": res["aggregate_metrics"]["accuracy"],
            "F1-Macro": res["aggregate_metrics"]["f1_macro"],
            "F1-Weighted": res["aggregate_metrics"]["f1_weighted"],
            "Ham F1": res["class_metrics"]["ham"]["f1_score"],
            "Spam Precision": res["class_metrics"]["spam"]["precision"],
            "Spam Recall": res["class_metrics"]["spam"]["recall"],
            "Spam F1": res["class_metrics"]["spam"]["f1_score"],
            "FPR (FP/N)": res["rates"]["false_positive_rate"],
            "Matriz Confusión": cm_str,
        })
    return pd.DataFrame(rows)

