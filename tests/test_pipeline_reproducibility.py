"""Pruebas automatizadas de reproducibilidad, serialización y validación del pipeline NLP/ML.

SMS Sentinel: Detección de Spam y Phishing en SMS mediante NLP y Machine Learning.
"""

import json
import os
import tempfile
from pathlib import Path
import joblib
import numpy as np
import pytest
from sklearn.pipeline import Pipeline

from src.models.evaluate import (
    evaluate_model,
    format_metrics_table,
    perform_qualitative_error_analysis,
)
from src.nlp.pipeline_builder import (
    build_sms_pipeline,
    inspect_pipeline_prediction,
    preprocess_for_pipeline,
)


@pytest.fixture
def sample_sms_data():
    """Muestras controladas de mensajes SMS para pruebas deterministas."""
    texts = [
        "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456",
        "GANA un premio de 5000 euros ahora mismo enviando PREMIO al 7788 ya!",
        "Hola mamá, llego a cenar a las ocho de la noche, compra pan por favor",
        "¿Nos vemos mañana en la universidad para el proyecto de software?",
        "AVISO IMPORTANTE: Transferencia de $1,500 retenida. Haga clic en http://verificar-pago.es",
        "Buenas tardes Alex, adjunto la minuta de la reunión de tópicos de ayer",
    ]
    labels = ["spam", "spam", "ham", "ham", "spam", "ham"]
    return texts, labels


def test_preprocess_for_pipeline_module_level():
    """Valida que preprocess_for_pipeline esté definida a nivel de módulo y funcione."""
    text = "Gana 1000 euros en http://promo.com llama al 912345678"
    processed = preprocess_for_pipeline(text)
    assert isinstance(processed, str)
    assert "TOKEN_URL" in processed
    assert "TOKEN_TEL" in processed
    assert "TOKEN_NUM" in processed


def test_pipeline_builder_structure():
    """Valida la arquitectura y etapas del pipeline de scikit-learn."""
    pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.1, max_features=1000)
    assert isinstance(pipe, Pipeline)
    assert "tfidf" in pipe.named_steps
    assert "classifier" in pipe.named_steps

    vectorizer = pipe.named_steps["tfidf"]
    assert vectorizer.ngram_range == (1, 2)
    assert vectorizer.sublinear_tf is True
    assert vectorizer.max_features == 1000


def test_pipeline_deterministic_fit_and_predict(sample_sms_data):
    """Valida determinismo estricto: dos ajustes con mismos datos producen idénticas predicciones."""
    texts, labels = sample_sms_data
    pipe1 = build_sms_pipeline(classifier_type="logistic_regression", C=1.0, random_state=42)
    pipe2 = build_sms_pipeline(classifier_type="logistic_regression", C=1.0, random_state=42)

    pipe1.fit(texts, labels)
    pipe2.fit(texts, labels)

    preds1 = pipe1.predict(texts)
    preds2 = pipe2.predict(texts)
    assert np.array_equal(preds1, preds2)

    probas1 = pipe1.predict_proba(texts)
    probas2 = pipe2.predict_proba(texts)
    assert np.allclose(probas1, probas2, atol=1e-6)


def test_pipeline_joblib_serialization(sample_sms_data):
    """Valida que el pipeline pueda serializarse a .joblib y cargarse sin perder fidelidad."""
    texts, labels = sample_sms_data
    pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.1)
    pipe.fit(texts, labels)

    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        joblib.dump(pipe, tmp_path)
        assert os.path.exists(tmp_path)
        assert os.path.getsize(tmp_path) > 0

        loaded_pipe = joblib.load(tmp_path)
        assert isinstance(loaded_pipe, Pipeline)

        orig_preds = pipe.predict(texts)
        loaded_preds = loaded_pipe.predict(texts)
        assert np.array_equal(orig_preds, loaded_preds)

        orig_probas = pipe.predict_proba(texts)
        loaded_probas = loaded_pipe.predict_proba(texts)
        assert np.allclose(orig_probas, loaded_probas, atol=1e-6)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_pipeline_inference_synthetic_tokens(sample_sms_data):
    """Valida que el pipeline infiera directamente a partir de texto crudo con entidades."""
    texts, labels = sample_sms_data
    pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.1)
    pipe.fit(texts, labels)

    # Inferencia en texto crudo
    phishing_sms = "ALERTA URGENTE: cuenta suspendida. Ingrese a http://banco-falso.com o llame al 912345678"
    legit_sms = "Hola amigo, ¿vamos por un café hoy por la tarde?"

    pred_phish = pipe.predict([phishing_sms])[0]
    pred_legit = pipe.predict([legit_sms])[0]

    assert pred_phish in ["ham", "spam"]
    assert pred_legit in ["ham", "spam"]


def test_inspect_pipeline_prediction(sample_sms_data):
    """Valida la función de trazabilidad y explicabilidad paso a paso del pipeline."""
    texts, labels = sample_sms_data
    pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.1)
    pipe.fit(texts, labels)

    raw_sms = "URGENTE: Gana $500 haciendo clic en http://sorteo.com ahora"
    trace = inspect_pipeline_prediction(pipe, raw_sms)

    assert "raw_text" in trace
    assert "normalized_text" in trace
    assert "tokens" in trace
    assert "filtered_tokens" in trace
    assert "stemmed_tokens" in trace
    assert "feature_weights" in trace
    assert "prediction" in trace
    assert "probabilities" in trace

    assert trace["prediction"] in ["ham", "spam"]
    assert "ham" in trace["probabilities"]
    assert "spam" in trace["probabilities"]
    assert pytest.approx(sum(trace["probabilities"].values()), 0.01) == 1.0


def test_evaluate_model_and_error_analysis(sample_sms_data):
    """Valida el cálculo de métricas de evaluación y análisis cualitativo de errores."""
    texts, labels = sample_sms_data
    pipe = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.1)
    pipe.fit(texts, labels)

    eval_result = evaluate_model(pipe, texts, labels, model_name="TestNB")

    assert "confusion_matrix" in eval_result
    assert "rates" in eval_result
    assert "class_metrics" in eval_result
    assert "aggregate_metrics" in eval_result
    assert 0.0 <= eval_result["rates"]["false_positive_rate"] <= 1.0
    assert 0.0 <= eval_result["aggregate_metrics"]["accuracy"] <= 1.0

    err_analysis = perform_qualitative_error_analysis(pipe, texts, labels, max_samples=3)
    assert "false_positives" in err_analysis
    assert "false_negatives" in err_analysis
    assert isinstance(err_analysis["false_positives"], list)
    assert isinstance(err_analysis["false_negatives"], list)

    table_df = format_metrics_table([eval_result])
    assert not table_df.empty
    assert "Modelo" in table_df.columns
    assert "F1-Macro" in table_df.columns


def test_serialized_production_pipeline_on_disk():
    """Valida la existencia y operabilidad del modelo final serializado en models/."""
    model_path = Path("models/spam_detector_pipeline.joblib")
    assert model_path.exists(), "El archivo 'models/spam_detector_pipeline.joblib' debe existir."
    assert model_path.stat().st_size > 1024, "El modelo serializado no debe ser un archivo vacío."

    pipeline = joblib.load(model_path)
    assert isinstance(pipeline, Pipeline)

    # Inferencia de prueba en frío
    test_texts = [
        "¿Has ganado 1,000 euros en efectivo o un premio! Para reclamar llame ya al 905000032",
        "Hola mamá, llego a casa a las 7 para cenar",
    ]
    preds = pipeline.predict(test_texts)
    assert len(preds) == 2
    assert preds[0] == "spam"
    assert preds[1] == "ham"


def test_production_metrics_json_on_disk():
    """Valida el esquema y criterios mínimos de calidad en models/metrics.json."""
    metrics_path = Path("models/metrics.json")
    assert metrics_path.exists(), "El archivo 'models/metrics.json' debe existir."

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert "winner_model" in data
    assert "winner_metrics" in data
    assert "qualitative_error_analysis" in data
    assert "benchmark_summary" in data

    winner_metrics = data["winner_metrics"]
    assert winner_metrics["aggregate_metrics"]["f1_macro"] >= 0.90
    assert winner_metrics["rates"]["false_positive_rate"] <= 0.05
    assert len(data["qualitative_error_analysis"]["false_positives"]) >= 3
    assert len(data["qualitative_error_analysis"]["false_negatives"]) >= 3


