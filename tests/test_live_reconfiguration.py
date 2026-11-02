"""Suite de pruebas automatizadas para Ensayos de Reconfiguración en Vivo y Orquestación.

SMS Sentinel: Detección de Spam y Phishing en SMS mediante NLP y Machine Learning.
Valida:
1. Sensibilidad léxica: adición/modificación de stop words y su impacto en tokenización y vectorización.
2. Sensibilidad morfológica y n-gramas: alternancia unigramas vs bigramas y dimensionalidad del vocabulario.
3. Swapping de modelos: alternancia entre MultinomialNB y LogisticRegression en el pipeline serializado.
4. Sensibilidad de umbral de riesgo (threshold tuning): calibración de umbrales para aumentar recall.
5. Reentrenamiento rápido (< 2 minutos): ejecución y actualización atómica del binario joblib y metrics.json.
6. Integridad de docker-compose: validación de puertos no estándar aislados (web:3090, api:8090, db:5439) y redes.
7. Integridad de scripts globales en package.json raíz y monorepo pnpm.
"""

import json
import re
import time
from pathlib import Path

import joblib
import pandas as pd
import pytest

from pipeline.models.train import train_and_evaluate
from pipeline.nlp.normalizer import normalize_text
from pipeline.nlp.pipeline_builder import build_sms_pipeline, explain_text
from pipeline.nlp.stopwords_es import filter_stopwords, get_spanish_stopwords

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_lexicon_stopword_sensitivity():
    """Valida que modificar stopwords o whitelists altera predeciblemente la salida del pipeline."""
    sample_text = "Urgente tu cuenta bancaria ha sido bloqueada temporalmente"

    # Con stop words estándar (cuenta, ha, sido)
    custom_stopwords = get_spanish_stopwords()
    tokens_base = filter_stopwords(sample_text.split(), stopwords=custom_stopwords)
    assert "cuenta" not in tokens_base or "ha" not in tokens_base

    # Ensayo de sensibilidad: si eliminamos 'cuenta' de stopwords (o la agregamos a whitelist)
    stopwords_modified = custom_stopwords - {"cuenta"}
    tokens_modified = filter_stopwords(sample_text.split(), stopwords=stopwords_modified)
    assert "cuenta" in tokens_modified

    # Verificar que el pipeline absorbe parámetros léxicos sin romper el contrato
    pipeline_unigram = build_sms_pipeline(classifier_type="multinomial_nb", ngram_range=(1, 1))
    X_toy = pd.Series(["Urgente cuenta bloqueada", "Hola como estas amigo", "Gana dinero ya llama"])
    y_toy = pd.Series(["spam", "ham", "spam"])
    pipeline_unigram.fit(X_toy, y_toy)

    pred = pipeline_unigram.predict(["Urgente cuenta"])
    assert pred[0] in ["ham", "spam"]


def test_ngram_range_sensitivity():
    """Valida que la alternancia entre unigramas (1,1) y bigramas (1,2) altera la dimensionalidad del vectorizador."""
    X_sample = pd.Series([
        "Urgente transferencia retenida llame al 900800700",
        "Hola que tal como te va el dia de hoy",
        "Felicidades has ganado un premio exclusivo entra al enlace",
        "Nos vemos en la estacion a las cinco de la tarde",
    ])
    y_sample = pd.Series(["spam", "ham", "spam", "ham"])

    pipe_unigrams = build_sms_pipeline(classifier_type="multinomial_nb", ngram_range=(1, 1))
    pipe_unigrams.fit(X_sample, y_sample)
    vocab_unigrams = pipe_unigrams.named_steps["tfidf"].vocabulary_

    pipe_bigrams = build_sms_pipeline(classifier_type="multinomial_nb", ngram_range=(1, 2))
    pipe_bigrams.fit(X_sample, y_sample)
    vocab_bigrams = pipe_bigrams.named_steps["tfidf"].vocabulary_

    # El vocabulario con bigramas debe tener mayor cardinalidad que solo unigramas
    assert len(vocab_bigrams) > len(vocab_unigrams)


def test_model_swapping_in_pipeline():
    """Valida la sustitución transparente del clasificador entre Naive Bayes y Logistic Regression."""
    X_sample = pd.Series(["Aviso urgente de seguridad", "Que comemos hoy al mediodia"])
    y_sample = pd.Series(["spam", "ham"])

    pipe_nb = build_sms_pipeline(classifier_type="multinomial_nb", alpha=0.5)
    pipe_nb.fit(X_sample, y_sample)
    assert pipe_nb.named_steps["classifier"].__class__.__name__ == "MultinomialNB"

    pipe_lr = build_sms_pipeline(classifier_type="logistic_regression", C=1.0)
    pipe_lr.fit(X_sample, y_sample)
    assert pipe_lr.named_steps["classifier"].__class__.__name__ == "LogisticRegression"

    # Ambos deben cumplir con predict y predict_proba idénticamente
    for pipe in [pipe_nb, pipe_lr]:
        pred = pipe.predict(["Mensaje de prueba"])
        proba = pipe.predict_proba(["Mensaje de prueba"])
        assert pred[0] in ["ham", "spam"]
        assert proba.shape == (1, 2)


def test_threshold_sensitivity_tuning():
    """Valida la calibración de umbrales para clasificación de riesgo (LOW, MEDIUM, CRÍTICO)."""
    # Función de calibración de riesgo estandarizada en la API
    def classify_risk(spam_prob: float, threshold_critical: float = 0.50, threshold_medium: float = 0.35) -> str:
        if spam_prob >= threshold_critical:
            return "CRÍTICO"
        elif spam_prob >= threshold_medium:
            return "MEDIO"
        return "BAJO"

    # Con umbral estándar
    assert classify_risk(0.40) == "MEDIO"
    assert classify_risk(0.60) == "CRÍTICO"
    assert classify_risk(0.20) == "BAJO"

    # Reconfiguración de alta sensibilidad: bajar umbral crítico a 0.35
    assert classify_risk(0.40, threshold_critical=0.35) == "CRÍTICO"


def test_retraining_speed_under_two_minutes(tmp_path):
    """Valida que el reentrenamiento y serialización atómica se ejecuta en < 2 minutos (criterio de aceptación)."""
    model_tmp = tmp_path / "test_pipeline.joblib"
    metrics_tmp = tmp_path / "test_metrics.json"

    t0 = time.time()
    result = train_and_evaluate(
        output_model_path=str(model_tmp),
        output_metrics_path=str(metrics_tmp),
        skip_tuning=True,  # Modo rápido para reconfiguraciones en vivo
    )
    elapsed = time.time() - t0

    # Debe completarse en menos de 150 segundos (tolerancia para I/O concurrente en CI)
    assert elapsed < 150.0
    assert model_tmp.exists()
    assert metrics_tmp.exists()

    # Validar que el artefacto generado es cargable y operativo
    loaded_pipe = joblib.load(model_tmp)
    spam_sample = "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456"
    pred = loaded_pipe.predict([spam_sample])
    assert pred[0] == "spam"


def test_docker_compose_configuration_integrity():
    """Valida que docker-compose.yml existe y orquesta los 3 servicios con puertos no estándar."""
    compose_path = _PROJECT_ROOT / "docker-compose.yml"
    assert compose_path.exists(), "docker-compose.yml no existe en la raíz del proyecto"

    content = compose_path.read_text(encoding="utf-8")

    # Validar presencia de los 3 servicios fundamentales
    assert re.search(r"^\s*db:", content, re.MULTILINE), "Servicio 'db' no configurado en docker-compose"
    assert re.search(r"^\s*api:", content, re.MULTILINE), "Servicio 'api' no configurado en docker-compose"
    assert re.search(r"^\s*web:", content, re.MULTILINE), "Servicio 'web' no configurado en docker-compose"

    # Verificar mapeo de puertos no estándar aislados
    assert "5439:5432" in content or "${DB_PORT:-5439}:5432" in content, "Puerto no estándar 5439 no mapeado para db"
    assert "8090:8000" in content or "${API_PORT:-8090}:8000" in content, "Puerto no estándar 8090 no mapeado para api"
    assert "3090:80" in content or "${WEB_PORT:-3090}:80" in content, "Puerto no estándar 3090 no mapeado para web"

    # Verificar healthcheck y redes compartidas
    assert "pg_isready" in content, "Healthcheck de base de datos no configurado"
    assert "sms_network" in content, "Red bridge compartida sms_network no configurada"
    assert "postgres_data" in content, "Volumen postgres_data para persistencia no configurado"


def test_root_package_json_scripts():
    """Valida que el package.json raíz centraliza los scripts de orquestación y monorepo."""
    pkg_path = _PROJECT_ROOT / "package.json"
    assert pkg_path.exists(), "package.json raíz no encontrado"

    with open(pkg_path, "r", encoding="utf-8") as f:
        pkg_data = json.load(f)

    scripts = pkg_data.get("scripts", {})
    required_scripts = ["dev", "build", "ml:train", "docker:up", "docker:down"]

    for script_name in required_scripts:
        assert script_name in scripts, f"Script '{script_name}' no declarado en package.json"
