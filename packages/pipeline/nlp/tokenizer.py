"""Módulo de tokenización y trazabilidad de transformaciones NLP para SMS Sentinel.

Provee tokenización boundary-safe que preserva intactos los tokens sintéticos
(TOKEN_URL, TOKEN_TEL, TOKEN_NUM), lematización/stemming morfológico en español
y un inspector paso a paso de transformaciones intermedias.
"""

import re
from typing import Any, Final, Literal, Optional

from pipeline.nlp.normalizer import (
    SYNTHETIC_TOKENS,
    TOKEN_NUM,
    TOKEN_TEL,
    TOKEN_URL,
    normalize_text,
)
from pipeline.nlp.stopwords_es import filter_stopwords, get_spanish_stopwords

# Patrón boundary-safe que extrae palabras respetando tokens sintéticos con guiones bajos
_TOKEN_PATTERN: Final[re.Pattern] = re.compile(
    rf"{TOKEN_URL}|{TOKEN_TEL}|{TOKEN_NUM}|[a-záéíóúüñA-ZÁÉÍÓÚÜÑ0-9]+",
    re.IGNORECASE,
)


def tokenize_text(text: str, apply_normalizer: bool = False) -> list[str]:
    """Tokeniza el texto preservando la integridad de tokens sintéticos.
    
    Parámetros:
        text: Cadena de entrada (normalizada o cruda).
        apply_normalizer: Si es True, ejecuta primero normalize_text().
    
    Retorna:
        Lista de tokens limpios respetando las fronteras léxicas.
    """
    if not text or not isinstance(text, str):
        return []

    target_text = normalize_text(text) if apply_normalizer else text
    matches = _TOKEN_PATTERN.findall(target_text)

    # Asegurar que los tokens sintéticos mantengan su forma canónica en mayúsculas
    result: list[str] = []
    for token in matches:
        upper_tok = token.upper()
        if upper_tok in SYNTHETIC_TOKENS:
            result.append(upper_tok)
        else:
            result.append(token.lower())

    return result


def stem_tokens(
    tokens: list[str],
    stemmer: Optional[Any] = None,
) -> list[str]:
    """Aplica reducción morfológica (stemming) en español sobre los tokens.
    
    Los tokens sintéticos (TOKEN_URL, TOKEN_TEL, TOKEN_NUM) se preservan intactos
    y jamás sufren recortes de sufijos.
    
    Parámetros:
        tokens: Lista de tokens.
        stemmer: Instancia de stemmer (por defecto SnowballStemmer('spanish')).
    
    Retorna:
        Lista de tokens con sus raíces morfológicas reducidas.
    """
    if not tokens:
        return []

    if stemmer is None:
        try:
            from nltk.stem import SnowballStemmer
            stemmer = SnowballStemmer("spanish")
        except Exception:
            stemmer = None

    if stemmer is None:
        # Si el stemmer no está disponible, retornar tokens originales
        return list(tokens)

    stemmed: list[str] = []
    for token in tokens:
        if token in SYNTHETIC_TOKENS:
            stemmed.append(token)
        else:
            stemmed.append(stemmer.stem(token))

    return stemmed


# Mapeo canónico léxico de lemas en español para términos críticos de SMS / Smishing
_SPANISH_LEMMA_MAP: Final[dict[str, str]] = {
    # Acciones y verbos de urgencia / banca
    "bloqueada": "bloquear",
    "bloqueado": "bloquear",
    "bloqueadas": "bloquear",
    "bloqueados": "bloquear",
    "bloqueo": "bloquear",
    "bloquearon": "bloquear",
    "ingrese": "ingresar",
    "ingresa": "ingresar",
    "ingresando": "ingresar",
    "ingresaron": "ingresar",
    "ingresen": "ingresar",
    "verifique": "verificar",
    "verifica": "verificar",
    "verificando": "verificar",
    "verificacion": "verificar",
    "verifican": "verificar",
    "verificado": "verificar",
    "actualice": "actualizar",
    "actualiza": "actualizar",
    "actualizando": "actualizar",
    "actualizacion": "actualizar",
    "ganaste": "ganar",
    "ganado": "ganar",
    "ganador": "ganar",
    "ganadora": "ganar",
    "ganadores": "ganar",
    "gana": "ganar",
    "ganas": "ganar",
    "ganaron": "ganar",
    "reclama": "reclamar",
    "reclame": "reclamar",
    "reclamando": "reclamar",
    "llame": "llamar",
    "llama": "llamar",
    "llamando": "llamar",
    "llamada": "llamar",
    "llamadas": "llamar",
    "transfiera": "transferir",
    "transfiere": "transferir",
    "transferido": "transferir",
    "transferencia": "transferencia",
    "transferencias": "transferencia",
    "suspenda": "suspender",
    "suspendido": "suspender",
    "suspendida": "suspender",
    "suspension": "suspender",
    "cancele": "cancelar",
    "cancela": "cancelar",
    "cancelado": "cancelar",
    "cancelada": "cancelar",
    "comuniquese": "comunicar",
    "comunica": "comunicar",
    "comunicaron": "comunicar",
    "confirme": "confirmar",
    "confirma": "confirmar",
    "confirmado": "confirmar",
    "confirmada": "confirmar",
    "solicite": "solicitar",
    "solicita": "solicitar",
    "solicitado": "solicitar",
    "solicitud": "solicitud",
    "solicitudes": "solicitud",
    # Sustantivos y entidades en plural
    "cuentas": "cuenta",
    "tarjetas": "tarjeta",
    "mensajes": "mensaje",
    "servicios": "servicio",
    "codigos": "codigo",
    "premios": "premio",
    "enlaces": "enlace",
    "datos": "dato",
    "claves": "clave",
    "bancos": "banco",
    "usuarios": "usuario",
    "alertas": "alerta",
    "notificaciones": "notificacion",
}


def lemmatize_tokens(tokens: list[str]) -> list[str]:
    """Aplica lematización canónica morfológica en español sobre los tokens.
    
    A diferencia de stemming (recorte algorítmico de sufijos que puede generar
    pseudo-raíces no gramaticales como 'bloque' o 'gan'), la lematización devuelve
    la forma léxica canónica de diccionario ('bloquear', 'ganar', 'cuenta').
    Los tokens sintéticos (TOKEN_URL, TOKEN_TEL, TOKEN_NUM) se preservan intactos.
    
    Parámetros:
        tokens: Lista de tokens filtrados.
        
    Retorna:
        Lista de tokens reducidos a su lema canónico en español.
    """
    if not tokens:
        return []

    lemmas: list[str] = []
    for token in tokens:
        if token in SYNTHETIC_TOKENS:
            lemmas.append(token)
            continue

        lower_tok = token.lower()
        if lower_tok in _SPANISH_LEMMA_MAP:
            lemmas.append(_SPANISH_LEMMA_MAP[lower_tok])
            continue

        # Reducción morfológica estándar de plurales en español
        word = lower_tok
        if len(word) > 4:
            if word.endswith("ces"):
                word = word[:-3] + "z"
            elif word.endswith("es") and word[-3] not in "aeiou":
                word = word[:-2]
            elif word.endswith("s") and word[-2] in "aeiou":
                word = word[:-1]

        lemmas.append(word)

    return lemmas


def preprocess_text(
    text: str,
    stem: bool = True,
    morphology: Literal["stemming", "lemmatization", "none"] = "stemming",
    stopwords: Optional[set[str]] = None,
) -> str:
    """Ejecuta el ciclo completo de preprocesamiento y devuelve el texto procesado.
    
    Apto para uso directo como preprocessor en scikit-learn o inferencia directa.
    
    Secuencia:
        1. Normalización y enmascaramiento regex.
        2. Tokenización boundary-safe.
        3. Filtrado de stopwords con whitelist.
        4. Reducción morfológica (según parámetro morphology o stem).
        5. Reensamblado en cadena de texto separada por espacios.
    """
    if not text or not isinstance(text, str):
        return ""

    normalized = normalize_text(text)
    tokens = tokenize_text(normalized)
    filtered = filter_stopwords(tokens, stopwords=stopwords)

    # Determinar estrategia de morfología
    if not stem and morphology == "stemming":
        morph_mode = "none"
    else:
        morph_mode = morphology

    if morph_mode == "stemming":
        final_tokens = stem_tokens(filtered)
    elif morph_mode == "lemmatization":
        final_tokens = lemmatize_tokens(filtered)
    else:
        final_tokens = filtered

    return " ".join(final_tokens)


def inspect_nlp_pipeline(
    text: str,
    stemmer: Optional[Any] = None,
    vectorizer: Optional[Any] = None,
    stopwords: Optional[set[str]] = None,
) -> dict[str, Any]:
    """Genera la traza completa de inspección paso a paso para un mensaje de entrada.
    
    Provee las 6 fases de visualización requeridas por la especificación de explicabilidad:
        1. raw_text: Texto original recibido.
        2. normalized_text: Texto tras regex y enmascaramiento sintético.
        3. tokens: Unidades léxicas extraídas de forma boundary-safe.
        4. filtered_tokens: Tokens tras depuración de stopwords (con whitelist activa).
        5. stemmed_tokens: Tokens tras normalización morfológica (Snowball).
        6. feature_weights: Diccionario de {término: peso TF-IDF} si se provee vectorizador.
    """
    raw_text = text if isinstance(text, str) else ""
    normalized_text = normalize_text(raw_text)
    tokens = tokenize_text(normalized_text)
    filtered_tokens = filter_stopwords(tokens, stopwords=stopwords)
    stemmed = stem_tokens(filtered_tokens, stemmer=stemmer)
    lemmatized = lemmatize_tokens(filtered_tokens)

    feature_weights: dict[str, float] = {}
    if vectorizer is not None and stemmed:
        try:
            processed_str = " ".join(stemmed)
            tfidf_vec = vectorizer.transform([processed_str])
            feature_names = vectorizer.get_feature_names_out()
            coo = tfidf_vec.tocoo()
            for col, val in zip(coo.col, coo.data):
                feature_weights[str(feature_names[col])] = round(float(val), 4)
        except Exception:
            pass

    return {
        "raw_text": raw_text,
        "normalized_text": normalized_text,
        "tokens": tokens,
        "filtered_tokens": filtered_tokens,
        "stemmed_tokens": stemmed,
        "lemmatized_tokens": lemmatized,
        "feature_weights": feature_weights,
    }
