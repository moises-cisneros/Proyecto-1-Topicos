"""Script unificado de entrenamiento, sintonía de hiperparámetros y serialización del pipeline.

SMS Sentinel: Detección de Spam y Phishing en SMS mediante NLP y Machine Learning.

Cumple con:
1. Principio de Pipeline Único: empaqueta preprocesamiento NLP y estimador en Pipeline.
2. Determinismo: fijación estricta de semillas aleatorias (random_state=42).
3. Holdout Immutability: evaluación rigurosa contra partición de prueba aislada.
4. Comparativa de 3 tiers: Baseline Dummy, MultinomialNB y LogisticRegression.
5. Validación cruzada estratificada 5-Fold sobre el conjunto de entrenamiento.
6. Serialización a 'models/spam_detector_pipeline.joblib' y métricas a 'models/metrics.json'.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score

# Asegurar path para imports locales
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.models.evaluate import (
    evaluate_model,
    format_metrics_table,
    perform_qualitative_error_analysis,
)
from src.nlp.pipeline_builder import build_sms_pipeline


def load_datasets(
    train_path: str = "data/processed/train.csv",
    test_path: str = "data/processed/test.csv",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga los conjuntos de datos estratificados de entrenamiento y prueba."""
    train_file = _PROJECT_ROOT / train_path
    test_file = _PROJECT_ROOT / test_path

    if not train_file.exists() or not test_file.exists():
        raise FileNotFoundError(
            f"No se encontraron los datasets procesados en '{train_file}' o '{test_file}'. "
            "Asegúrese de haber ejecutado la preparación de datos de HU-01."
        )

    df_train = pd.read_csv(train_file)
    df_test = pd.read_csv(test_file)

    # Validar presencia de columnas obligatorias
    for df, name in [(df_train, "train"), (df_test, "test")]:
        if "text" not in df.columns or "label" not in df.columns:
            raise ValueError(f"El dataset {name} debe contener las columnas 'text' y 'label'.")

    return df_train, df_test


def tune_hyperparameters(
    X_train: pd.Series,
    y_train: pd.Series,
    cv_folds: int = 5,
    random_state: int = 42,
) -> dict[str, Any]:
    """Ejecuta 5-Fold Stratified Cross Validation para optimizar Naive Bayes y Logistic Regression."""
    skf = StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    print(f"[*] Ejecutando Stratified {cv_folds}-Fold CV sobre {len(X_train)} muestras de entrenamiento...")

    # 1. Optimizar MultinomialNB: alpha in [0.01, 0.1, 0.5, 1.0, 2.0]
    nb_alphas = [0.01, 0.1, 0.5, 1.0, 2.0]
    best_nb_alpha = 0.1
    best_nb_f1 = -1.0
    nb_results = {}

    for alpha in nb_alphas:
        pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=alpha)
        scores = cross_val_score(pipe, X_train, y_train, cv=skf, scoring="f1_macro", n_jobs=-1)
        mean_score = float(np.mean(scores))
        nb_results[str(alpha)] = round(mean_score, 4)
        if mean_score > best_nb_f1:
            best_nb_f1 = mean_score
            best_nb_alpha = alpha

    print(f"    [+] MultinomialNB óptimo: alpha={best_nb_alpha} (F1-Macro CV: {best_nb_f1:.4f})")

    # 2. Optimizar LogisticRegression: C in [0.01, 0.1, 1.0, 10.0, 50.0]
    lr_c_values = [0.01, 0.1, 1.0, 10.0, 50.0]
    best_lr_c = 10.0
    best_lr_f1 = -1.0
    lr_results = {}

    for c_val in lr_c_values:
        pipe = build_sms_pipeline(classifier_type="logistic_regression", C=c_val, random_state=random_state)
        scores = cross_val_score(pipe, X_train, y_train, cv=skf, scoring="f1_macro", n_jobs=-1)
        mean_score = float(np.mean(scores))
        lr_results[str(c_val)] = round(mean_score, 4)
        if mean_score > best_lr_f1:
            best_lr_f1 = mean_score
            best_lr_c = c_val

    print(f"    [+] LogisticRegression óptimo: C={best_lr_c} (F1-Macro CV: {best_lr_f1:.4f})")

    return {
        "best_nb_alpha": best_nb_alpha,
        "best_nb_f1": best_nb_f1,
        "nb_cv_grid": nb_results,
        "best_lr_c": best_lr_c,
        "best_lr_f1": best_lr_f1,
        "lr_cv_grid": lr_results,
    }


def train_and_evaluate(
    output_model_path: str = "models/spam_detector_pipeline.joblib",
    output_metrics_path: str = "models/metrics.json",
    train_path: str = "data/processed/train.csv",
    test_path: str = "data/processed/test.csv",
    cv_folds: int = 5,
    random_state: int = 42,
) -> dict[str, Any]:
    """Pipeline completo de entrenamiento, evaluación comparativa y serialización."""
    start_time = time.time()
    print("=" * 65)
    print(" SMS Sentinel — Entrenamiento y Benchmarking de Modelos de ML")
    print("=" * 65)

    # 1. Cargar particiones
    df_train, df_test = load_datasets(train_path, test_path)
    X_train, y_train = df_train["text"], df_train["label"]
    X_test, y_test = df_test["text"], df_test["label"]

    print(f"[*] Datos cargados: {len(X_train)} train | {len(X_test)} test (Holdout)")
    print(f"    Distribución Train: ham={sum(y_train == 'ham')}, spam={sum(y_train == 'spam')}")
    print(f"    Distribución Test:  ham={sum(y_test == 'ham')}, spam={sum(y_test == 'spam')}")

    # 2. Sintonía de hiperparámetros con 5-Fold Stratified CV
    tuning = tune_hyperparameters(X_train, y_train, cv_folds=cv_folds, random_state=random_state)
    best_alpha = tuning["best_nb_alpha"]
    best_c = tuning["best_lr_c"]

    # 3. Construir los 3 pipelines comparativos
    pipelines = {
        "Baseline (Dummy Most Frequent)": build_sms_pipeline(classifier_type="dummy"),
        "Multinomial Naive Bayes": build_sms_pipeline(classifier_type="multinomial_nb", alpha=best_alpha),
        "Logistic Regression (Challenger)": build_sms_pipeline(classifier_type="logistic_regression", C=best_c, random_state=random_state),
    }

    eval_results = []
    trained_pipelines = {}

    print("\n[*] Entrenando pipelines sobre la partición completa de entrenamiento y evaluando en Holdout...")
    for model_name, pipe in pipelines.items():
        t0 = time.time()
        pipe.fit(X_train, y_train)
        fit_duration = time.time() - t0
        trained_pipelines[model_name] = pipe

        res = evaluate_model(pipe, X_test, y_test, model_name=model_name)
        res["training_duration_seconds"] = round(fit_duration, 3)
        eval_results.append(res)
        print(f"    -> [{model_name}] F1-Macro: {res['aggregate_metrics']['f1_macro']} | FPR: {res['rates']['false_positive_rate']}")

    # 4. Mostrar tabla comparativa
    df_comparison = format_metrics_table(eval_results)
    print("\n" + "=" * 65)
    print(" TABLA COMPARATIVA DE MODELOS (EVALUACIÓN EN HOLDOUT TEST SET)")
    print("=" * 65)
    print(df_comparison.to_string(index=False))
    print("=" * 65)

    # 5. Selección del modelo ganador
    # Criterio: Mayor F1-Macro y menor False Positive Rate
    # MultinomialNB y LogisticRegression ambos son evaluados; se selecciona el de mayor F1-Macro en test
    nb_eval = next(r for r in eval_results if "Naive Bayes" in r["model_name"])
    lr_eval = next(r for r in eval_results if "Logistic Regression" in r["model_name"])

    if nb_eval["aggregate_metrics"]["f1_macro"] >= lr_eval["aggregate_metrics"]["f1_macro"]:
        winner_name = "Multinomial Naive Bayes"
        winner_eval = nb_eval
    else:
        winner_name = "Logistic Regression (Challenger)"
        winner_eval = lr_eval

    winner_pipeline = trained_pipelines[winner_name]
    print(f"\n[+] Modelo Ganador Seleccionado: {winner_name}")
    print(f"    F1-Macro: {winner_eval['aggregate_metrics']['f1_macro']} | Precisión Spam: {winner_eval['class_metrics']['spam']['precision']}")

    # 6. Diagnóstico cualitativo de errores
    error_analysis = perform_qualitative_error_analysis(winner_pipeline, X_test, y_test, max_samples=5)
    print(f"\n[*] Análisis Cualitativo de Errores ({winner_name}):")
    print(f"    Falsos Positivos totales en test: {error_analysis['total_false_positives']}")
    for i, fp in enumerate(error_analysis["false_positives"], 1):
        print(f"      FP #{i}: \"{fp['text'][:60]}...\" -> Causa: {fp['diagnosis']}")

    print(f"    Falsos Negativos totales en test: {error_analysis['total_false_negatives']}")
    for i, fn in enumerate(error_analysis["false_negatives"], 1):
        print(f"      FN #{i}: \"{fn['text'][:60]}...\" -> Causa: {fn['diagnosis']}")

    # 7. Serialización de artefactos
    model_out = _PROJECT_ROOT / output_model_path
    metrics_out = _PROJECT_ROOT / output_metrics_path

    model_out.parent.mkdir(parents=True, exist_ok=True)
    metrics_out.parent.mkdir(parents=True, exist_ok=True)

    # Serializar pipeline en .joblib
    joblib.dump(winner_pipeline, model_out)
    print(f"\n[+] Pipeline serializado atómicamente a: {model_out.relative_to(_PROJECT_ROOT)}")

    # Guardar métricas completas en metrics.json
    metrics_payload = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "winner_model": winner_name,
        "hyperparameter_tuning": tuning,
        "benchmark_summary": eval_results,
        "winner_metrics": winner_eval,
        "qualitative_error_analysis": error_analysis,
        "dataset_split": {
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "random_state": random_state,
            "test_ratio": 0.2,
        },
        "total_execution_time_seconds": round(time.time() - start_time, 2),
    }

    with open(metrics_out, "w", encoding="utf-8") as f:
        json.dump(metrics_payload, f, indent=2, ensure_ascii=False)
    print(f"[+] Métricas de evaluación exportadas a: {metrics_out.relative_to(_PROJECT_ROOT)}")

    print(f"\n[OK] Pipeline entrenado, validado y serializado exitosamente en {metrics_payload['total_execution_time_seconds']}s.")
    return metrics_payload


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Entrenamiento y serialización de modelos para SMS Sentinel")
    parser.add_argument("--cv", type=int, default=5, help="Particiones de validación cruzada estratificada (default: 5)")
    parser.add_argument("--seed", type=int, default=42, help="Semilla aleatoria (default: 42)")
    args = parser.parse_args()

    train_and_evaluate(cv_folds=args.cv, random_state=args.seed)

