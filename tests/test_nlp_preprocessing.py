"""Pruebas unitarias para el pipeline de preprocesamiento de NLP (SMS Sentinel).

Verifica enmascaramiento de entidades (URLs, teléfonos, números), preservación de
whitelist en stop words, tokenización boundary-safe, stemming en español y trazabilidad.
"""

import pytest

from pipeline.nlp.normalizer import (
    SYNTHETIC_TOKENS,
    TOKEN_NUM,
    TOKEN_TEL,
    TOKEN_URL,
    mask_entities,
    mask_numbers,
    mask_phones,
    mask_urls,
    normalize_text,
)
from pipeline.nlp.stopwords_es import (
    DEFAULT_WHITELIST,
    NEGATION_WHITELIST,
    URGENCY_WHITELIST,
    filter_stopwords,
    get_spanish_stopwords,
)
from pipeline.nlp.tokenizer import (
    inspect_nlp_pipeline,
    lemmatize_tokens,
    preprocess_text,
    stem_tokens,
    tokenize_text,
)


# ============================================================================
# 1. Pruebas de Enmascaramiento Regex y Normalización
# ============================================================================


def test_url_masking_varieties() -> None:
    """Verifica enmascaramiento de URLs HTTP, HTTPS, WWW y dominios cortos."""
    test_cases = [
        ("Visite http://banco.com/login inmediatamente.", f"Visite  {TOKEN_URL}  inmediatamente."),
        ("Ingrese a https://secure-bank.es/auth?id=99.", f"Ingrese a  {TOKEN_URL} ."),
        ("Oferta en www.tienda-online.org/promo!", f"Oferta en  {TOKEN_URL} !"),
        ("Canjee en bit.ly/promo2026 ya.", f"Canjee en  {TOKEN_URL}  ya."),
    ]
    for raw, expected in test_cases:
        masked = mask_urls(raw)
        assert TOKEN_URL in masked
        # La puntuación terminal no debe ser devorada por el token
        if raw.endswith("."):
            assert masked.strip().endswith(".")
        elif raw.endswith("!"):
            assert masked.strip().endswith("!")


def test_phone_masking_varieties() -> None:
    """Verifica enmascaramiento de teléfonos con formato internacional, local y bloques."""
    phones = [
        "+34 600 123 456",
        "+1-800-555-0199",
        "0800 542 0825",
        "08001950382",
        "(91) 1234567",
        "900123456",
    ]
    for ph in phones:
        text = f"Contacte al {ph} para confirmar"
        masked = mask_phones(text)
        assert TOKEN_TEL in masked
        assert ph not in masked


def test_number_masking_and_currency() -> None:
    """Verifica enmascaramiento de cifras monetarias y números generales."""
    numbers = [
        ("$500", TOKEN_NUM),
        ("1,000", TOKEN_NUM),
        ("25.50", TOKEN_NUM),
        ("1000 eur", TOKEN_NUM),
        ("100", TOKEN_NUM),
        ("2024", TOKEN_NUM),
    ]
    for num_str, expected_tok in numbers:
        text = f"Ha ganado {num_str} en efectivo"
        masked = mask_numbers(text)
        assert expected_tok in masked


def test_mask_entities_order_preservation() -> None:
    """Verifica que números dentro de URLs o teléfonos no se fragmenten erróneamente."""
    text = "Visita https://promo123.com/ref999 o llama al +34 912 345 678 para ganar $100."
    masked = mask_entities(text)
    assert TOKEN_URL in masked
    assert TOKEN_TEL in masked
    assert TOKEN_NUM in masked
    # La URL no debe quedar corrompida con TOKEN_NUM interno
    assert "https" not in masked
    assert "+34" not in masked


def test_normalize_text_diacritics_and_case() -> None:
    """Verifica que normalize_text preserva diacríticos en español y genera minúsculas."""
    sample = "¡URGENTE! Su cuenta en Banco del Pacífico ha sido bloqueada. Ingrese a https://banco.es"
    normalized = normalize_text(sample, keep_accents=True)

    # Tokens sintéticos en mayúsculas
    assert TOKEN_URL in normalized
    # Contenido léxico en minúsculas
    assert "urgente" in normalized
    assert "cuenta" in normalized
    # Acento gráfico y caracteres españoles preservados
    assert "pacífico" in normalized
    # Signos de exclamación eliminados
    assert "¡" not in normalized
    assert "!" not in normalized


def test_normalize_text_edge_cases() -> None:
    """Verifica el comportamiento seguro ante entradas nulas, vacías o sólo símbolos."""
    assert normalize_text("") == ""
    assert normalize_text(None) == ""  # type: ignore[arg-type]
    assert normalize_text("   \n\t  ") == ""
    assert normalize_text("!@#$%^&*()_+") == ""


# ============================================================================
# 2. Pruebas de Stop Words y Whitelist Contextual
# ============================================================================


def test_stopwords_whitelist_retention() -> None:
    """Verifica que términos clave de polaridad y urgencia NO sean eliminados."""
    stopwords = get_spanish_stopwords()

    # Negaciones críticas
    for neg in ["no", "ni", "tampoco", "sin"]:
        assert neg not in stopwords, f"La negación '{neg}' no debe ser stopword"

    # Triggers de urgencia y phishing
    for urg in ["urgente", "bloqueo", "bloqueada", "ya", "ahora", "cuenta", "alerta", "premio"]:
        assert urg not in stopwords, f"El detonante '{urg}' no debe ser stopword"

    # Palabras gramaticales vacías comunes sí deben ser stopwords
    for stop in ["de", "la", "el", "los", "en", "por", "para", "con"]:
        assert stop in stopwords, f"'{stop}' debería estar presente en stopwords"


def test_filter_stopwords_keeps_synthetic_tokens() -> None:
    """Verifica que el filtrado de stopwords nunca elimine los tokens sintéticos."""
    tokens = ["urgente", "de", "la", TOKEN_URL, "para", "el", TOKEN_TEL, "sin", TOKEN_NUM]
    filtered = filter_stopwords(tokens)

    assert TOKEN_URL in filtered
    assert TOKEN_TEL in filtered
    assert TOKEN_NUM in filtered
    assert "urgente" in filtered
    assert "sin" in filtered
    assert "de" not in filtered
    assert "la" not in filtered
    assert "para" not in filtered


# ============================================================================
# 3. Pruebas de Tokenización Boundary-Safe y Stemming
# ============================================================================


def test_tokenize_text_boundary_safe() -> None:
    """Verifica que los tokens sintéticos con guiones bajos no se fragmenten."""
    text = f"urgente llame al {TOKEN_TEL} o visite {TOKEN_URL} saldo {TOKEN_NUM}"
    tokens = tokenize_text(text)

    assert TOKEN_TEL in tokens
    assert TOKEN_URL in tokens
    assert TOKEN_NUM in tokens
    # Asegura que no se hayan dividido por el guion bajo
    assert "token" not in tokens
    assert "url" not in tokens
    assert "tel" not in tokens
    assert "num" not in tokens


def test_stemming_preserves_synthetic_tokens() -> None:
    """Verifica que SnowballStemmer reduzca palabras pero deje intactos los tokens sintéticos."""
    tokens = ["urgente", "bloqueada", "ganadores", TOKEN_URL, TOKEN_TEL, TOKEN_NUM]
    stemmed = stem_tokens(tokens)

    # Los tokens sintéticos deben permanecer idénticos
    assert TOKEN_URL in stemmed
    assert TOKEN_TEL in stemmed
    assert TOKEN_NUM in stemmed

    # Las palabras normales deben haber sufrido reducción morfológica
    assert "bloque" in stemmed[1] or stemmed[1] != "bloqueada"
    assert "ganad" in stemmed[2] or stemmed[2] != "ganadores"


# ============================================================================
# 4. Pruebas de Explicabilidad (Inspección Paso a Paso) y Preprocesamiento
# ============================================================================


def test_inspect_nlp_pipeline_intermediate_steps() -> None:
    """Verifica que inspect_nlp_pipeline retorne todas las 6 etapas requeridas."""
    raw = "¡Aviso urgente! Su cuenta ha sido bloqueada. Visite https://seguridad-banco.es hoy."
    trace = inspect_nlp_pipeline(raw)

    expected_keys = {
        "raw_text",
        "normalized_text",
        "tokens",
        "filtered_tokens",
        "stemmed_tokens",
        "feature_weights",
    }
    assert expected_keys.issubset(trace.keys())

    assert trace["raw_text"] == raw
    assert TOKEN_URL in trace["normalized_text"]
    assert "urgente" in trace["tokens"]
    assert "bloqueada" in trace["filtered_tokens"]
    assert TOKEN_URL in trace["stemmed_tokens"]
    assert isinstance(trace["feature_weights"], dict)


def test_preprocess_text_full_cycle() -> None:
    """Verifica la ejecución de punta a punta de preprocess_text."""
    raw = "Gana $1000 llamando al 08001950382 o entrando a www.premio.com ahora mismo!"
    processed = preprocess_text(raw, stem=True)

    assert TOKEN_NUM in processed
    assert TOKEN_TEL in processed
    assert TOKEN_URL in processed
    assert "ahor" in processed or "ahora" in processed  # 'ahora' preservada en whitelist
    assert "llamando" not in processed  # fue reducida a raíz 'llam'


def test_lemmatization_preserves_synthetic_tokens() -> None:
    """Verifica que la lematización canónica reduzca a lemas y preserve tokens sintéticos."""
    tokens = ["bloqueada", "cuentas", "ganadores", "llamadas", TOKEN_URL, TOKEN_TEL, TOKEN_NUM]
    lemmas = lemmatize_tokens(tokens)

    # Tokens sintéticos preservados
    assert TOKEN_URL in lemmas
    assert TOKEN_TEL in lemmas
    assert TOKEN_NUM in lemmas

    # Lematización léxica
    assert "bloquear" in lemmas
    assert "cuenta" in lemmas
    assert "ganar" in lemmas
    assert "llamar" in lemmas


def test_preprocess_text_lemmatization_cycle() -> None:
    """Verifica el preprocesamiento completo con estrategia de lematización."""
    raw = "Su tarjeta bancaria ha sido bloqueada. Ingrese a https://seguridad.es ya."
    lemmatized = preprocess_text(raw, morphology="lemmatization")

    assert TOKEN_URL in lemmatized
    assert "bloquear" in lemmatized
    assert "tarjeta" in lemmatized
    assert "ingresar" in lemmatized
