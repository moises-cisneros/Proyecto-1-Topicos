"""Pruebas automatizadas de integración y unitarias para el endpoint de explicabilidad NLP.

Valida el contrato JSON del endpoint POST /nlp/debug, las 5 fases de transformación
secuencial (original -> normalizado -> tokens -> sin stopwords con whitelist -> raíces Snowball),
la extracción y ordenamiento de las top características TF-IDF y el manejo estricto de errores HTTP 422 y 503.
"""

from fastapi.testclient import TestClient
import pytest

from api.main import app
from pipeline.nlp.pipeline_builder import explain_text


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba FastAPI con ciclo de vida lifespan ejecutado."""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint_includes_nlp_debug_url(client: TestClient):
    """Verifica que la ruta raíz exponga el enlace al endpoint de depuración NLP."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "nlp_debug_url" in data
    assert data["nlp_debug_url"] == "/nlp/debug"


def test_nlp_debug_success_with_phishing_message(client: TestClient):
    """Verifica el desglose completo de explicabilidad en un mensaje malicioso con entidades."""
    text = (
        "URGENTE: Su tarjeta 9876 ha sido bloqueada. Llame al 900123456 o "
        "ingrese a https://banco-seguridad.com para reactivarla."
    )
    response = client.post("/nlp/debug", json={"text": text})
    assert response.status_code == 200
    data = response.json()

    # 1. Verificar presencia de todos los campos del contrato NLPDebugResponse
    assert "original" in data
    assert "normalized" in data
    assert "tokens" in data
    assert "no_stopwords" in data
    assert "stemmed_or_lemmatized" in data
    assert "tfidf_top_features" in data

    # 2. Paso 01: Texto original intacto
    assert data["original"] == text

    # 3. Paso 02: Enmascaramiento regex de entidades sintéticas
    norm = data["normalized"]
    assert "TOKEN_NUM" in norm
    assert "TOKEN_TEL" in norm
    assert "TOKEN_URL" in norm

    # 4. Paso 03: Tokenización boundary-safe
    tokens = data["tokens"]
    assert isinstance(tokens, list)
    assert "TOKEN_URL" in tokens
    assert "TOKEN_TEL" in tokens
    assert "TOKEN_NUM" in tokens
    assert "urgente" in tokens

    # 5. Paso 04: Stop words filtradas preservando whitelist (urgencia)
    no_sw = data["no_stopwords"]
    assert isinstance(no_sw, list)
    assert "urgente" in no_sw, "La whitelist debe preservar términos de urgencia"
    assert "TOKEN_URL" in no_sw
    assert "de" not in no_sw, "Stopwords estándar deben ser eliminadas"
    assert "al" not in no_sw

    # 6. Paso 05: Reducción morfológica Snowball respetando tokens sintéticos
    stems = data["stemmed_or_lemmatized"]
    assert isinstance(stems, list)
    assert "TOKEN_URL" in stems, "Tokens sintéticos no deben sufrir stemming"
    assert "TOKEN_TEL" in stems
    assert "urgent" in stems

    # 7. Paso 06: Top características TF-IDF ponderadas (máximo 5)
    tfidf_feats = data["tfidf_top_features"]
    assert isinstance(tfidf_feats, list)
    assert 1 <= len(tfidf_feats) <= 5

    # Verificar estructura y orden descendente de pesos
    weights = []
    for item in tfidf_feats:
        assert "feature" in item
        assert "weight" in item
        assert isinstance(item["feature"], str)
        assert isinstance(item["weight"], (int, float))
        assert item["weight"] > 0
        weights.append(item["weight"])

    assert weights == sorted(weights, reverse=True), "Los pesos deben estar ordenados descendentemente"


def test_nlp_debug_success_with_benign_message(client: TestClient):
    """Verifica el funcionamiento del debugger sobre un SMS legítimo cotidiano."""
    text = "Hola amigo, nos vemos a las 5 de la tarde en la plaza para tomar café."
    response = client.post("/nlp/debug", json={"text": text})
    assert response.status_code == 200
    data = response.json()

    assert data["original"] == text
    assert "TOKEN_URL" not in data["normalized"]
    assert "TOKEN_TEL" not in data["normalized"]
    assert isinstance(data["tokens"], list)
    assert len(data["tokens"]) > 0
    assert len(data["no_stopwords"]) < len(data["tokens"])
    assert isinstance(data["tfidf_top_features"], list)


def test_nlp_debug_empty_text_returns_422(client: TestClient):
    """Verifica que enviar texto vacío retorne error HTTP 422 de validación."""
    response = client.post("/nlp/debug", json={"text": ""})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_nlp_debug_whitespace_only_returns_422(client: TestClient):
    """Verifica que texto compuesto únicamente por espacios retorne HTTP 422."""
    response = client.post("/nlp/debug", json={"text": "     \n\t   "})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_nlp_debug_exceeding_length_returns_422(client: TestClient):
    """Verifica que mensajes mayores a 1000 caracteres sean rechazados con HTTP 422."""
    long_text = "alerta " * 200  # > 1000 caracteres
    response = client.post("/nlp/debug", json={"text": long_text})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_nlp_debug_missing_body_returns_422(client: TestClient):
    """Verifica que peticiones sin cuerpo JSON retornen HTTP 422."""
    response = client.post("/nlp/debug", json={})
    assert response.status_code == 422


def test_nlp_debug_service_unavailable_503(client: TestClient):
    """Verifica respuesta HTTP 503 cuando el pipeline no está disponible en memoria."""
    # Guardar pipeline actual
    saved_pipeline = getattr(app.state, "pipeline", None)
    try:
        app.state.pipeline = None
        response = client.post("/nlp/debug", json={"text": "Mensaje de prueba"})
        assert response.status_code == 503
        data = response.json()
        assert "no está disponible" in data["detail"]
    finally:
        app.state.pipeline = saved_pipeline


def test_explain_text_unit_function():
    """Prueba unitaria directa sobre la función explain_text con y sin pipeline."""
    # 1. Invocación estándar
    result = explain_text("URGENTE: Oferta especial en http://promo.com gana $500", top_n=3)
    assert result["original"] == "URGENTE: Oferta especial en http://promo.com gana $500"
    assert "TOKEN_URL" in result["normalized"]
    assert "TOKEN_NUM" in result["normalized"]
    assert isinstance(result["tokens"], list)
    assert isinstance(result["no_stopwords"], list)
    assert isinstance(result["stemmed_or_lemmatized"], list)
    assert len(result["tfidf_top_features"]) <= 3

    # 2. Manejo de texto vacío o tipos inválidos
    empty_res = explain_text("")
    assert empty_res["original"] == ""
    assert empty_res["tokens"] == []
    assert empty_res["tfidf_top_features"] == []
