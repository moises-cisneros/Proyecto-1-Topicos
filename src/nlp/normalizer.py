"""Módulo de normalización léxica y enmascaramiento de entidades para SMS en español.

Sustituye vectores críticos de spam/phishing (URLs, teléfonos, montos/números)
por tokens sintéticos canónicos y normaliza caracteres respetando la morfología
del español (tildes, eñes).
"""

import re
from typing import Final

TOKEN_URL: Final[str] = "TOKEN_URL"
TOKEN_TEL: Final[str] = "TOKEN_TEL"
TOKEN_NUM: Final[str] = "TOKEN_NUM"

SYNTHETIC_TOKENS: Final[set[str]] = {TOKEN_URL, TOKEN_TEL, TOKEN_NUM}

# Regex para detección de URLs y dominios web
_URL_REGEX = re.compile(
    r"https?://\S+|www\.\S+|\b[a-zA-Z0-9.-]+\.[a-z]{2,}(?:/[^\s]*)?",
    re.IGNORECASE,
)

# Regex para números telefónicos (internacionales, nacionales, con separadores o bloques continuos >= 7 dígitos)
_PHONE_REGEX = re.compile(
    r"(?:\+\d{1,3}[\s.-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}\b"
    r"|\+\d{1,4}[\s.-]?\d{4,12}\b"
    r"|\b\d{7,14}\b",
    re.IGNORECASE,
)

# Regex para montos monetarios y expresiones numéricas/cantidades
_NUM_REGEX = re.compile(
    r"[$€£¥]\s*\d+(?:[.,]\d+)?"
    r"|\b\d+(?:[.,]\d+)?\s*(?:[$€£¥]|usd|eur|bs\.?|pesos)\b"
    r"|\b\d+(?:[.,]\d+)?\b",
    re.IGNORECASE,
)

# Signos de puntuación terminal que deben despegarse de URLs antes de enmascarar
_TRAILING_PUNCT = ".,;:!?)\"'>]}"


def mask_urls(text: str) -> str:
    """Enmascara URLs y enlaces web con TOKEN_URL preservando la puntuación exterior."""
    if not text:
        return ""

    def _replace_url(match: re.Match) -> str:
        url = match.group(0)
        trailing = ""
        while url and url[-1] in _TRAILING_PUNCT:
            trailing = url[-1] + trailing
            url = url[:-1]
        return f" {TOKEN_URL} " + trailing

    return _URL_REGEX.sub(_replace_url, text)


def mask_phones(text: str) -> str:
    """Enmascara números telefónicos con TOKEN_TEL evitando colisión con tokens sintéticos."""
    if not text:
        return ""
    return _PHONE_REGEX.sub(f" {TOKEN_TEL} ", text)


def mask_numbers(text: str) -> str:
    """Enmascara montos y secuencias numéricas con TOKEN_NUM respetando tokens sintéticos."""
    if not text:
        return ""

    # No enmascarar números que formen parte de tokens sintéticos ya sustituidos
    def _replace_num(match: re.Match) -> str:
        val = match.group(0)
        # Si coincide con un token sintético ya existente, preservarlo
        if val in SYNTHETIC_TOKENS:
            return val
        return f" {TOKEN_NUM} "

    return _NUM_REGEX.sub(_replace_num, text)


def mask_entities(text: str) -> str:
    """Aplica secuencialmente el enmascaramiento de URLs, teléfonos y números.
    
    El orden estricto (URL -> Teléfono -> Número) evita que los componentes numéricos
    de URLs o teléfonos sean fragmentados prematuramente.
    """
    if not text or not isinstance(text, str):
        return ""

    text = mask_urls(text)
    text = mask_phones(text)
    text = mask_numbers(text)
    return text


def normalize_text(text: str, keep_accents: bool = True) -> str:
    """Normaliza texto aplicando enmascaramiento de entidades, minúsculas y limpieza de ruido.
    
    Parámetros:
        text: Cadena de texto de entrada.
        keep_accents: Si es True, preserva acentos gráficos en español (á, é, í, ó, ú, ü, ñ).
                      Si es False, descompone diacríticos a caracteres ASCII base.
    
    Retorna:
        Texto normalizado con tokens sintéticos en mayúsculas (TOKEN_URL, TOKEN_TEL, TOKEN_NUM)
        y palabras en minúsculas sin símbolos espurios.
    """
    if not text or not isinstance(text, str):
        return ""

    # 1. Enmascarar entidades críticas
    masked = mask_entities(text)

    # 2. Proteger tokens sintéticos antes de aplicar minúsculas y filtrado de puntuación
    protected = masked.replace(TOKEN_URL, " __TOKEN_URL__ ")
    protected = protected.replace(TOKEN_TEL, " __TOKEN_TEL__ ")
    protected = protected.replace(TOKEN_NUM, " __TOKEN_NUM__ ")

    # 3. Conversión a minúsculas para el contenido léxico
    lowered = protected.lower()

    # 4. Limpieza de puntuación y símbolos ruidosos
    if keep_accents:
        # Permitir caracteres alfabéticos en español, dígitos residuales, guiones bajos para tokens y espacios
        cleaned = re.sub(r"[^a-záéíóúüñ_0-9\s]", " ", lowered)
    else:
        # Opcional: remover tildes si el vectorizador o configuración lo requiere
        import unicodedata
        nfkd = unicodedata.normalize("NFKD", lowered)
        stripped = "".join(c for c in nfkd if not unicodedata.combining(c) or c in ("\u0303",))  # preservar eñe si posible
        cleaned = re.sub(r"[^a-zñ_0-9\s]", " ", stripped)

    # 5. Restaurar tokens sintéticos canónicos en mayúsculas
    restored = cleaned.replace("__token_url__", TOKEN_URL)
    restored = restored.replace("__token_tel__", TOKEN_TEL)
    restored = restored.replace("__token_num__", TOKEN_NUM)

    # 6. Colapsar espacios múltiples y recortar extremos
    normalized = re.sub(r"\s+", " ", restored).strip()
    return normalized
