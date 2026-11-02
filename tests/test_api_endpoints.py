"""Pruebas automatizadas de integración y validación para la API REST de SMS Sentinel.

Valida los contratos de esquemas, endpoints /health, /predict, /predict/batch, /metrics,
respuestas HTTP 422 ante entradas inválidas y tiempos de latencia.
"""

import io
from fastapi.testclient import TestClient
import pytest

from api.main import app


@pytest.fixture(scope="module")
def client():
    """Cliente de prueba de FastAPI con ciclo de vida lifespan ejecutado."""
    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client: TestClient):
    """Verifica que la ruta raíz responda con estado 200 y enlaces a documentación."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["service"] == "SMS Sentinel API"
    assert "docs_url" in data


def test_health_endpoint(client: TestClient):
    """Verifica el estado de salud y que el modelo de ML esté cargado en memoria."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "UP"
    assert data["model_loaded"] is True
    assert isinstance(data["model_name"], str)
    assert data["version"] == "1.0.0"
    assert "timestamp" in data


def test_predict_ham_message(client: TestClient):
    """Verifica la clasificación correcta de un mensaje legítimo (ham)."""
    payload = {"text": "Hola mamá, llego a cenar a las ocho de la noche, compra pan por favor."}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "ham"
    assert data["ham_probability"] > 0.50
    assert data["spam_probability"] < 0.50
    assert data["risk_level"] == "BAJO"
    assert data["latency_ms"] >= 0
    assert abs((data["spam_probability"] + data["ham_probability"]) - 1.0) < 0.01


def test_predict_spam_message(client: TestClient):
    """Verifica la clasificación correcta de un mensaje malicioso (spam/phishing)."""
    payload = {
        "text": "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456"
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "spam"
    assert data["spam_probability"] > 0.50
    assert data["risk_level"] in ("MEDIO", "CRÍTICO")
    assert "TOKEN_URL" in data["detected_tokens"]
    assert "TOKEN_TEL" in data["detected_tokens"]


def test_predict_empty_text_validation_422(client: TestClient):
    """Verifica que un texto vacío sea rechazado con HTTP 422."""
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_predict_whitespace_text_validation_422(client: TestClient):
    """Verifica que un texto de solo espacios sea rechazado con HTTP 422."""
    response = client.post("/predict", json={"text": "     \t \n   "})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_predict_too_long_text_validation_422(client: TestClient):
    """Verifica que un texto superior a 1000 caracteres sea rechazado con HTTP 422."""
    long_text = "A" * 1001
    response = client.post("/predict", json={"text": long_text})
    assert response.status_code == 422


def test_predict_missing_payload_422(client: TestClient):
    """Verifica que un payload vacío o sin campo 'text' sea rechazado con HTTP 422."""
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_batch_predict_json(client: TestClient):
    """Verifica el procesamiento masivo vía JSON devolviendo sumario y predicciones."""
    payload = {
        "messages": [
            {"text": "Nos vemos en la facultad mañana para estudiar."},
            {"text": "GANA 5000 EUROS YA! Haz clic en http://premio-facil.es ahora."},
            {"text": "¿Tienes tiempo para revisar el informe hoy?"},
        ]
    }
    response = client.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    summary = data["summary"]
    assert summary["total"] == 3
    assert summary["spam_count"] >= 1
    assert summary["ham_count"] >= 1
    assert summary["total"] == summary["spam_count"] + summary["ham_count"]
    assert len(data["predictions"]) == 3
    assert data["predictions"][0]["text"] == "Nos vemos en la facultad mañana para estudiar."
    assert data["predictions"][1]["text"] == "GANA 5000 EUROS YA! Haz clic en http://premio-facil.es ahora."
    assert data["total_latency_ms"] > 0


def test_batch_predict_empty_list_422(client: TestClient):
    """Verifica que un lote sin mensajes sea rechazado con HTTP 422."""
    response = client.post("/predict/batch", json={"messages": []})
    assert response.status_code == 422


def test_batch_predict_csv_upload(client: TestClient):
    """Verifica la clasificación de un archivo CSV con columna de texto."""
    csv_content = (
        "text\n"
        "Hola amigo cómo estás\n"
        "Premio exclusivo de 1000 dólares en http://ganadores.com reclama ya\n"
        "Te llamo más tarde cuando termine la clase\n"
    )
    files = {"file": ("mensajes_prueba.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
    response = client.post("/predict/batch/csv", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total"] == 3
    assert data["summary"]["spam_count"] >= 1
    assert data["summary"]["ham_count"] >= 1
    assert len(data["predictions"]) == 3
    assert data["predictions"][0]["text"] == "Hola amigo cómo estás"
    assert data["predictions"][1]["text"] == "Premio exclusivo de 1000 dólares en http://ganadores.com reclama ya"


def test_batch_predict_csv_invalid_extension_422(client: TestClient):
    """Verifica que un archivo no CSV sea rechazado con HTTP 422."""
    fake_file = {"file": ("archivo.txt", io.BytesIO(b"contenido texto"), "text/plain")}
    response = client.post("/predict/batch/csv", files=fake_file)
    assert response.status_code == 422


def test_metrics_endpoint(client: TestClient):
    """Verifica la disponibilidad de las métricas de evaluación del modelo."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "winner_model" in data
    assert "hyperparameter_tuning" in data
    assert "benchmark_summary" in data
    assert isinstance(data["benchmark_summary"], list)


def test_predict_latency_performance(client: TestClient):
    """Verifica que el tiempo de inferencia individual sea menor a 20 ms."""
    payload = {"text": "Mensaje de prueba para medición de latencia en microservicio."}
    latencies = []
    for _ in range(5):
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
        latencies.append(response.json()["latency_ms"])
    avg_latency = sum(latencies) / len(latencies)
    assert avg_latency < 20.0, f"Latencia promedio ({avg_latency} ms) excede el umbral objetivo."
