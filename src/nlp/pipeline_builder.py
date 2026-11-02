"""Constructor de Pipelines scikit-learn para clasificación de SMS en SMS Sentinel.

Garantiza el Principio de Pipeline Único: el preprocesamiento de texto
(normalización regex, tokens sintéticos, filtrado con whitelist y Snowball stemming)
se integra de manera atómica con TfidfVectorizer y el estimador supervisado,
permitiendo que el pipeline serializado en .joblib reciba directamente cadenas
de texto crudo tanto en entrenamiento como en inferencia de producción.
"""

from pathlib import Path
from typing import Any, Literal, Optional, Union
import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

from src.nlp.normalizer import normalize_text
from src.nlp.stopwords_es import filter_stopwords
from src.nlp.tokenizer import (
    inspect_nlp_pipeline,
    preprocess_text,
    stem_tokens,
    tokenize_text,
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


def explain_text(
    text: str,
    pipeline: Optional[Pipeline] = None,
    top_n: int = 5,
) -> dict[str, Any]:
    """Desglosa las transformaciones intermedias de NLP y extrae las top características TF-IDF.
    
    Captura de forma secuencial los 5 estados intermedios del procesamiento de texto:
    1. original: Texto crudo recibido.
    2. normalized: Texto tras regex y enmascaramiento con tokens sintéticos.
    3. tokens: Lista de unidades léxicas tokenizadas boundary-safe.
    4. no_stopwords: Tokens tras depuración de stopwords preservando whitelist.
    5. stemmed_or_lemmatized: Tokens morfológicamente reducidos con Snowball stemming.
    
    Adicionalmente extrae las top_n características con mayor peso numérico en el
    vector TF-IDF sublineal para el mensaje evaluado.
    
    Parámetros:
        text: Cadena de texto a procesar.
        pipeline: Instancia opcional de scikit-learn Pipeline (o TfidfVectorizer).
        top_n: Cantidad máxima de términos TF-IDF destacados a extraer (por defecto 5).
        
    Retorna:
        Diccionario con las claves 'original', 'normalized', 'tokens', 'no_stopwords',
        'stemmed_or_lemmatized' y 'tfidf_top_features'.
    """
    raw_text = text if isinstance(text, str) else ""
    normalized = normalize_text(raw_text)
    tokens = tokenize_text(normalized)
    no_stopwords = filter_stopwords(tokens)
    stemmed_or_lemmatized = stem_tokens(no_stopwords)

    vectorizer = None
    if pipeline is not None:
        if isinstance(pipeline, Pipeline):
            vectorizer = pipeline.named_steps.get("tfidf")
        elif hasattr(pipeline, "transform"):
            vectorizer = pipeline
    else:
        # Intentar cargar pipeline entrenado por defecto si existe en disco
        default_model_path = Path("models/spam_detector_pipeline.joblib")
        if default_model_path.exists():
            try:
                import joblib
                loaded_model = joblib.load(default_model_path)
                if isinstance(loaded_model, Pipeline):
                    vectorizer = loaded_model.named_steps.get("tfidf")
            except Exception:
                vectorizer = None

    tfidf_top_features: list[dict[str, Any]] = []
    if vectorizer is not None and hasattr(vectorizer, "transform") and raw_text.strip():
        try:
            tfidf_vec = vectorizer.transform([raw_text])
            feature_names = vectorizer.get_feature_names_out()
            coo = tfidf_vec.tocoo()
            sorted_feats = sorted(zip(coo.col, coo.data), key=lambda x: x[1], reverse=True)
            for col, val in sorted_feats[:top_n]:
                tfidf_top_features.append({
                    "feature": str(feature_names[col]),
                    "weight": round(float(val), 4),
                })
        except Exception:
            tfidf_top_features = []

    return {
        "original": raw_text,
        "normalized": normalized,
        "tokens": tokens,
        "no_stopwords": no_stopwords,
        "stemmed_or_lemmatized": stemmed_or_lemmatized,
        "tfidf_top_features": tfidf_top_features,
    }


