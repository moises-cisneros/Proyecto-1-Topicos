"""Pruebas automatizadas de persistencia transaccional y auditoría en base de datos.

Valida:
1. Inserción transaccional de auditoría en cada llamada a /predict.
2. Inserción de lotes procesados en /predict/batch.
3. Consulta y paginación en el endpoint GET /history.
4. Degradación elegante de /predict y /history ante desconexión o fallo de base de datos.
5. Reporte de conectividad de base de datos en GET /health.
"""

from datetime import datetime
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base, get_db
from api.main import app
from api.models_db import MessageAudit


# Configurar SQLite en memoria para pruebas aisladas y deterministas
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos limpia en memoria para cada función de prueba."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client_with_db(db_session):
    """Cliente de prueba de FastAPI con dependencia get_db sobreescrita con la BD de prueba."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_without_db():
    """Cliente de prueba simulando desconexión o fallo total de la base de datos."""
    def override_get_db_disconnected():
        yield None

    app.dependency_overrides[get_db] = override_get_db_disconnected
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_predict_persists_audit_record(client_with_db: TestClient, db_session):
    """Verifica que una llamada exitosa a /predict inserte un registro en message_audits."""
    payload = {
        "text": "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456"
    }
    response = client_with_db.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "spam"

    # Verificar registro en la base de datos
    records = db_session.query(MessageAudit).all()
    assert len(records) == 1
    audit = records[0]
    assert audit.message_text == payload["text"]
    assert audit.prediction == data["label"]
    assert audit.probability_spam == data["spam_probability"]
    assert audit.probability_ham == data["ham_probability"]
    assert audit.risk_level == data["risk_level"]
    assert "TOKEN_URL" in audit.detected_tokens
    assert audit.latency_ms >= 0
    assert isinstance(audit.created_at, datetime)


def test_predict_batch_persists_all_records(client_with_db: TestClient, db_session):
    """Verifica que las consultas en lote por JSON persistan la totalidad de los mensajes."""
    payload = {
        "messages": [
            {"text": "Hola amigo, nos vemos a las ocho para cenar."},
            {"text": "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456"},
        ]
    }
    response = client_with_db.post("/predict/batch", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["summary"]["total"] == 2

    # Verificar que ambos registros están en BD
    records = db_session.query(MessageAudit).all()
    assert len(records) == 2
    predictions = [r.prediction for r in records]
    assert "ham" in predictions
    assert "spam" in predictions


def test_get_history_empty(client_with_db: TestClient):
    """Verifica que /history retorne lista vacía cuando no hay registros."""
    response = client_with_db.get("/history")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["limit"] == 50
    assert data["offset"] == 0
    assert data["records"] == []


def test_get_history_pagination_and_sorting(client_with_db: TestClient, db_session):
    """Verifica la paginación y orden descendente cronológico en /history."""
    # Insertar 5 registros con marcas de tiempo explícitas
    for i in range(1, 6):
        record = MessageAudit(
            message_text=f"Mensaje de prueba número {i}",
            prediction="ham" if i % 2 == 0 else "spam",
            probability_spam=0.1 if i % 2 == 0 else 0.9,
            probability_ham=0.9 if i % 2 == 0 else 0.1,
            risk_level="BAJO" if i % 2 == 0 else "CRÍTICO",
            detected_tokens=[],
            latency_ms=2.5,
        )
        db_session.add(record)
    db_session.commit()

    # Página 1: limit=2, offset=0
    res_p1 = client_with_db.get("/history?limit=2&offset=0")
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert data_p1["total"] == 5
    assert len(data_p1["records"]) == 2
    assert data_p1["records"][0]["id"] == 5
    assert data_p1["records"][1]["id"] == 4

    # Página 2: limit=2, offset=2
    res_p2 = client_with_db.get("/history?limit=2&offset=2")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["records"]) == 2
    assert data_p2["records"][0]["id"] == 3
    assert data_p2["records"][1]["id"] == 2

    # Página 3: limit=2, offset=4
    res_p3 = client_with_db.get("/history?limit=2&offset=4")
    assert res_p3.status_code == 200
    data_p3 = res_p3.json()
    assert len(data_p3["records"]) == 1
    assert data_p3["records"][0]["id"] == 1


def test_graceful_degradation_when_db_is_down(client_without_db: TestClient):
    """Verifica que la API continúe prediciendo si la base de datos está caída."""
    payload = {
        "text": "URGENTE: Su cuenta bancaria ha sido bloqueada. Ingrese a http://banco-alerta.com o llame al 900123456"
    }
    response = client_without_db.post("/predict", json=payload)
    
    # La inferencia debe completarse con éxito a pesar de que no haya BD
    assert response.status_code == 200
    data = response.json()
    assert data["label"] == "spam"
    assert data["risk_level"] in ("MEDIO", "CRÍTICO")

    # /history debe degradar elegantemente retornando 0 registros sin arrojar HTTP 500
    history_res = client_without_db.get("/history")
    assert history_res.status_code == 200
    history_data = history_res.json()
    assert history_data["total"] == 0
    assert history_data["records"] == []


def test_health_check_reports_database_status(client_with_db: TestClient):
    """Verifica que /health incluya el campo database_connected."""
    response = client_with_db.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "database_connected" in data
    assert isinstance(data["database_connected"], bool)
