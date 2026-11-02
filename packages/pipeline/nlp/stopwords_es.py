"""Gestión de stop words en español con whitelist contextual de polaridad y urgencia.

Preserva términos críticos para la detección de phishing y spam tales como negaciones
("no", "sin") y detonantes de urgencia/llamada a la acción ("urgente", "bloqueo", "ya").
"""

from typing import Final, Iterable, Optional
import warnings

# Whitelist de negaciones para preservar polaridad y cambios de sentido
NEGATION_WHITELIST: Final[set[str]] = {
    "no",
    "ni",
    "tampoco",
    "sin",
    "nada",
    "nunca",
    "jamas",
    "jamás",
}

# Whitelist de urgencia, seguridad y llamadas a la acción típicas en phishing/spam
URGENCY_WHITELIST: Final[set[str]] = {
    "urgente",
    "inmediato",
    "inmediata",
    "aviso",
    "bloqueo",
    "bloqueada",
    "bloqueado",
    "ya",
    "ahora",
    "cuenta",
    "alerta",
    "premio",
    "ganador",
    "banco",
    "seguridad",
    "clave",
    "contra",
    "estado",
    "importante",
    "verificar",
}

# Whitelist combinada por defecto
DEFAULT_WHITELIST: Final[set[str]] = NEGATION_WHITELIST | URGENCY_WHITELIST

# Lista de respaldo de stopwords comunes en español en caso de indisponibilidad de NLTK
_FALLBACK_SPANISH_STOPWORDS: Final[set[str]] = {
    "a", "al", "algo", "algunas", "algunos", "ante", "antes", "aquel", "aquellas",
    "aquellos", "aqui", "aquí", "arriba", "asi", "así", "atras", "aun", "aún",
    "bajo", "bastante", "bien", "cabe", "cada", "casi", "cerca", "cierta",
    "ciertas", "cierto", "ciertos", "como", "cómo", "con", "conmigo", "conseguimos",
    "conseguir", "consigo", "consigue", "consiguen", "consigues", "contigo",
    "cual", "cuál", "cuales", "cuáles", "cualquier", "cualquiera", "cualquieras",
    "cuan", "cuán", "cuando", "cuándo", "cuanta", "cuánta", "cuantas", "cuántas",
    "cuanto", "cuánto", "cuantos", "cuántos", "de", "dejar", "del", "demas",
    "demás", "demasiada", "demasiadas", "demasiado", "demasiados", "dentro",
    "desde", "donde", "dónde", "dos", "el", "él", "ella", "ellas", "ello",
    "ellos", "empleais", "emplean", "emplear", "empleas", "empleo", "en", "encima",
    "entonces", "entre", "era", "eramos", "éramos", "eran", "eras", "eres", "es",
    "esa", "esas", "ese", "eso", "esos", "esta", "estaba", "estaban", "estabas",
    "estad", "estada", "estadas", "estado", "estados", "estais", "estamos",
    "estan", "están", "estar", "estara", "estará", "estaran", "estarán", "estaras",
    "estarás", "estare", "estaré", "estareis", "estareis", "estaria", "estaría",
    "estarias", "estarías", "este", "esteis", "estemos", "esten", "estén", "estes",
    "estés", "esto", "estos", "estoy", "estuve", "estuviera", "estuvieran",
    "estuvieras", "estuvieron", "estuviese", "estuviesen", "estuvieses",
    "estuvimos", "estuviste", "estuvisteis", "estuvo", "fue", "fuera", "fueran",
    "fueras", "fueron", "fuese", "fuesen", "fueses", "fui", "fuimos", "fuiste",
    "fuisteis", "ha", "habeis", "habéis", "habia", "había", "habian", "habían",
    "habias", "habías", "habida", "habidas", "habido", "habidos", "habiendo",
    "habla", "hablan", "hablar", "hablas", "hablo", "habra", "habrá", "habran",
    "habrán", "habras", "habrás", "habre", "habré", "habreis", "habréis",
    "habria", "habría", "habrian", "habrían", "habrias", "habrías", "hace",
    "haceis", "hacéis", "hacemos", "hacen", "hacer", "hacerlo", "haces", "hacia",
    "hacía", "haciendo", "hago", "han", "has", "hasta", "hay", "haya", "hayais",
    "hayáis", "hayan", "hayas", "hayamos", "he", "hecho", "hemos", "hube",
    "hubiera", "hubieran", "hubieras", "hubieron", "hubiese", "hubiesen",
    "hubieses", "hubimos", "hubiste", "hubisteis", "hubo", "la", "las", "le",
    "les", "lo", "los", "mas", "más", "me", "mi", "mí", "mia", "mía", "mias",
    "mías", "mientras", "mio", "mío", "mios", "míos", "mis", "misma", "mismas",
    "mismo", "mismos", "modo", "mucha", "muchas", "mucho", "muchos", "muy",
    "nos", "nosotras", "nosotros", "nuestra", "nuestras", "nuestro", "nuestros",
    "o", "os", "otra", "otras", "otro", "otros", "para", "pero", "poca", "pocas",
    "poco", "pocos", "podeis", "podéis", "podemos", "poder", "podria", "podría",
    "podrian", "podrían", "podrias", "podrías", "por", "porque", "por qué",
    "primero", "puede", "pueden", "puedo", "pues", "que", "qué", "quien", "quién",
    "quienes", "quiénes", "quedo", "se", "segun", "según", "ser", "sera", "será",
    "seran", "serán", "seras", "serás", "sere", "seré", "sereis", "seréis",
    "seria", "sería", "serian", "serían", "serias", "serías", "si", "sí",
    "siempre", "siendo", "sobre", "sois", "solamente", "solo", "sólo", "somos",
    "son", "soy", "su", "sus", "suya", "suyas", "suyo", "suyos", "tal", "tales",
    "tambien", "también", "te", "teneis", "tenéis", "tenemos", "tener", "tenga",
    "tengais", "tengáis", "tengan", "tengas", "tengo", "tenia", "tenía", "tenian",
    "tenían", "tenias", "tenías", "tenida", "tenidas", "tenido", "tenidos",
    "teniendo", "tendra", "tendrá", "tendran", "tendrán", "tendras", "tendrás",
    "tendre", "tendré", "tendreis", "tendréis", "tendria", "tendría", "tendrian",
    "tendrían", "tendrias", "tendrías", "ti", "tiene", "tienen", "tienes", "toda",
    "todas", "todavia", "todavía", "todo", "todos", "tras", "tu", "tú", "tus",
    "tuve", "tuviera", "tuvieran", "tuvieras", "tuvieron", "tuviese", "tuviesen",
    "tuvieses", "tuvimos", "tuviste", "tuvisteis", "tuvo", "un", "una", "unas",
    "uno", "unos", "usa", "usais", "usáis", "usamos", "usan", "usar", "usas",
    "uso", "va", "vais", "vamos", "van", "vaya", "vayan", "vayas", "verdad",
    "verdadera", "verdadero", "vosotras", "vosotros", "voy", "vuestra", "vuestras",
    "vuestro", "vuestros", "y",
}


def load_raw_spanish_stopwords() -> set[str]:
    """Carga la lista base de stop words en español desde NLTK con respaldo interno."""
    try:
        from nltk.corpus import stopwords
        return set(stopwords.words("spanish"))
    except Exception as exc:
        warnings.warn(
            f"No se pudo cargar stopwords desde nltk.corpus ({exc}). Usando lista curada de respaldo.",
            UserWarning,
            stacklevel=2,
        )
        return set(_FALLBACK_SPANISH_STOPWORDS)


def get_spanish_stopwords(
    whitelist: Optional[Iterable[str]] = None,
    extra_stopwords: Optional[Iterable[str]] = None,
) -> set[str]:
    """Obtiene el conjunto de stopwords en español tras excluir la whitelist contextual.
    
    Parámetros:
        whitelist: Términos que NO deben ser eliminados (por defecto DEFAULT_WHITELIST).
        extra_stopwords: Términos adicionales a incorporar como stopwords.
    
    Retorna:
        Conjunto de stop words listo para usar en vectorizadores o filtrado manual.
    """
    raw_stops = load_raw_spanish_stopwords()
    active_whitelist = set(whitelist) if whitelist is not None else DEFAULT_WHITELIST

    # Excluir de stopwords todas las palabras presentes en la whitelist
    filtered_stops = raw_stops - active_whitelist

    # Incorporar stopwords adicionales si se especifican
    if extra_stopwords:
        filtered_stops |= (set(extra_stopwords) - active_whitelist)

    return filtered_stops


def filter_stopwords(
    tokens: list[str],
    stopwords: Optional[set[str]] = None,
) -> list[str]:
    """Filtra una lista de tokens eliminando stop words pero preservando tokens sintéticos.
    
    Parámetros:
        tokens: Lista de tokens a filtrar.
        stopwords: Conjunto de stop words a excluir. Si es None, usa get_spanish_stopwords().
    
    Retorna:
        Lista de tokens limpios.
    """
    if not tokens:
        return []

    if stopwords is None:
        stopwords = get_spanish_stopwords()

    from pipeline.nlp.normalizer import SYNTHETIC_TOKENS

    # Preservar tokens que no sean stopwords o que sean tokens sintéticos
    return [
        token for token in tokens
        if token in SYNTHETIC_TOKENS or token.lower() not in stopwords
    ]
