"""Constructor de Pipelines scikit-learn para clasificación de SMS en SMS Sentinel.

Garantiza el Principio de Pipeline Único: el preprocesamiento de texto
(normalización regex, tokens sintéticos, filtrado con whitelist y Snowball stemming)
se integra de manera atómica con TfidfVectorizer y el estimador supervisado,
permitiendo que el pipeline serializado en .joblib reciba directamente cadenas
de texto crudo tanto en entrenamiento como en inferencia de producción.
"""

from typing import Any, Literal, Optional, Union
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.nlp.tokenizer import (
    inspect_nlp_pipeline,
    preprocess_text,
)


def preprocess_for_pipeline(text: str) -> str:
    """Función de preprocesamiento canónica a nivel de módulo para scikit-learn.
    
    Al estar definida a nivel de módulo, garantiza 100% de serializabilidad
    con joblib/pickle sin errores de clausura o lambdas anónimas.
    """
    return preprocess_text(text, stem=True)


def build_sms_pipeline(
    classifier_type: Literal["multinomial_nb", "logistic_regression", "dummy"] = "multinomial_nb",
    alpha: float = 0.1,
    C: float = 10.0,
    max_features: int = 4000,
    ngram_range: tuple[int, int] = (1, 2),
    sublinear_tf: bool = True,
    random_state: int = 42,
    custom_classifier: Optional[Any] = None,
) -> Pipeline:
    """Construye un Pipeline de scikit-learn unificado para clasificación de SMS.
    
    Parámetros:
        classifier_type: Tipo de clasificador ('multinomial_nb', 'logistic_regression' o 'dummy').
        alpha: Parámetro de suavizado de Laplace para MultinomialNB.
        C: Parámetro de regularización inversa L2 para LogisticRegression.
        max_features: Límite superior de vocabulario TF-IDF para prevenir sobreajuste.
        ngram_range: Rango de n-gramas (por defecto (1, 2) para capturar bigramas clave).
        sublinear_tf: Si es True, aplica escala logarítmica 1 + log(tf) para atenuar repetición.
        random_state: Semilla fija para reproducibilidad determinista.
        custom_classifier: Estimador opcional provisto por el usuario para experimentación.
        
    Retorna:
        sklearn.pipeline.Pipeline listo para fit(), predict() y serialización joblib.
    """
    # 1. Configurar vectorizador TF-IDF con preprocesador atómico
    vectorizer = TfidfVectorizer(
        preprocessor=preprocess_for_pipeline,
        ngram_range=ngram_range,
        max_features=max_features,
        sublinear_tf=sublinear_tf,
    )

    # 2. Configurar clasificador
    if custom_classifier is not None:
        classifier = custom_classifier
    elif classifier_type in ("multinomial_nb", "naive_bayes", "nb"):
        classifier = MultinomialNB(alpha=alpha)
    elif classifier_type in ("logistic_regression", "lr"):
        classifier = LogisticRegression(
            C=C,
            max_iter=1000,
            random_state=random_state,
        )
    elif classifier_type == "dummy":
        classifier = DummyClassifier(strategy="most_frequent")
    else:
        raise ValueError(f"Tipo de clasificador no soportado: '{classifier_type}'")

    pipeline = Pipeline([
        ("tfidf", vectorizer),
        ("classifier", classifier),
    ])

    return pipeline


def inspect_pipeline_prediction(
    pipeline: Pipeline,
    raw_text: str,
) -> dict[str, Any]:
    """Inspecciona la predicción y el desglose de transformaciones para un SMS.
    
    Combina la trazabilidad paso a paso del pipeline NLP con la predicción
    y distribución de probabilidades del clasificador final.
    """
    vectorizer = pipeline.named_steps.get("tfidf")
    classifier = pipeline.named_steps.get("classifier")

    # Obtener traza explicable del módulo NLP
    trace = inspect_nlp_pipeline(raw_text, vectorizer=vectorizer)

    # Ejecutar predicción
    predicted_label = pipeline.predict([raw_text])[0]
    
    probabilities: dict[str, float] = {}
    if hasattr(classifier, "predict_proba"):
        classes = list(pipeline.classes_)
        proba_values = pipeline.predict_proba([raw_text])[0]
        for cls_name, prob in zip(classes, proba_values):
            probabilities[str(cls_name)] = float(prob)
    elif hasattr(classifier, "decision_function"):
        score = float(classifier.decision_function(vectorizer.transform([raw_text]))[0])
        probabilities["decision_score"] = score

    return {
        **trace,
        "prediction": str(predicted_label),
        "probabilities": probabilities,
    }

