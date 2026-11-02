"""Módulo de configuración y conexión a Base de Datos PostgreSQL con SQLAlchemy.

Configurado para operar en el puerto 5439 (local en Windows/Host) o 5432 (red Docker),
con connection pooling resiliente y degradación elegante si la base de datos no está disponible.
"""

import logging
import os
import re
import time
from pathlib import Path
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger("sms_sentinel.database")


def load_dotenv_file(dotenv_path: Optional[Path] = None) -> None:
    """Carga variables desde el archivo .env a os.environ si no fueron definidas previamente."""
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parent.parent / ".env"

    if not dotenv_path.exists():
        return

    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, val = line.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val
    except Exception as exc:
        logger.debug("No fue posible leer archivo .env: %s", exc)

# Cargar archivo .env
load_dotenv_file()


def resolve_database_url() -> str:
    """Resuelve la URL de PostgreSQL desde DATABASE_URL o la ensambla dinámicamente desde variables DB_*."""
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    user = os.getenv("DB_USER", "postgres")
    password = os.getenv("DB_PASSWORD", "postgres")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    dbname = os.getenv("DB_NAME", "sms_sentinel_db")

    auth = f"{user}:{password}" if password else user
    return f"postgresql://{auth}@{host}:{port}/{dbname}"


DATABASE_URL = resolve_database_url()

# Argumentos de conexión específicos según el motor
engine_kwargs = {
    "pool_pre_ping": True,  # Verifica validez de conexión antes de usarla
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Parámetros de Connection Pooling para PostgreSQL en alta concurrencia
    engine_kwargs.update({
        "poolclass": QueuePool,
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_recycle": int(os.getenv("DB_POOL_RECYCLE", "300")),
        "pool_timeout": float(os.getenv("DB_POOL_TIMEOUT", "2.0")),
        "connect_args": {"connect_timeout": 2},
    })

try:
    engine = create_engine(DATABASE_URL, **engine_kwargs)
except Exception as exc:
    logger.warning("No se pudo instanciar el engine con la URL configurada: %s. Creando engine con sqlite en memoria.", exc)
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

_last_check_time = 0.0
_last_check_status = False
_last_error_message = "Sin comprobación previa"


def check_db_connection(force: bool = False) -> bool:
    """Verifica si la base de datos está accesible y responde a consultas.
    
    Implementa un caché de 5 segundos para evitar sobrecarga de sondeo y latencias
    cuando el servidor de base de datos se encuentra inaccesible.
    """
    global _last_check_time, _last_check_status, _last_error_message
    now = time.monotonic()
    if not force and (now - _last_check_time < 5.0):
        return _last_check_status

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _last_check_status = True
        _last_error_message = ""
    except Exception as exc:
        raw_msg = str(exc).strip()
        clean_err = re.sub(r"\(Background on this error at: [^\)]+\)", "", raw_msg).strip()
        clean_err = re.sub(r"\[SQL:[^\]]+\]", "", clean_err).strip()

        # Limpieza de mensajes verbosos de psycopg2 / SQLAlchemy para facilitar diagnóstico
        if "password authentication failed" in clean_err.lower() or "la autentificación password falló" in clean_err.lower():
            _last_error_message = "Fallo de autenticación: contraseña o usuario incorrecto para PostgreSQL en .env"
        elif "connection refused" in clean_err.lower() or "conexión rechazada" in clean_err.lower():
            _last_error_message = "Conexión rechazada: el servicio PostgreSQL no responde en el host/puerto especificado"
        elif "database" in clean_err.lower() and "does not exist" in clean_err.lower():
            _last_error_message = "Base de datos no encontrada: cree la base de datos indicada en DB_NAME"
        elif "operationalerror" in clean_err.lower() and len(clean_err.replace("(psycopg2.OperationalError)", "").strip()) == 0:
            target_host = DATABASE_URL.split("@")[-1] if "@" in DATABASE_URL else "PostgreSQL"
            _last_error_message = f"Fallo de conexión o autenticación en {target_host} (verifique usuario y DB_PASSWORD en .env)"
        else:
            _last_error_message = clean_err or exc.__class__.__name__

        logger.debug("Comprobación de conexión a BD fallida: %s", _last_error_message)
        _last_check_status = False
    
    _last_check_time = now
    return _last_check_status


def init_db() -> bool:
    """Inicializa el esquema de base de datos creando las tablas si no existen.
    
    Retorna True si las tablas se crearon satisfactoriamente, False si no hubo conexión.
    No arroja excepciones no controladas para garantizar degradación elegante.
    """
    if not check_db_connection(force=True):
        logger.warning(
            "Base de datos no disponible al iniciar (%s). Las tablas se crearán automáticamente al reconectar.",
            _last_error_message,
        )
        return False

    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Esquema de base de datos inicializado exitosamente.")
        return True
    except Exception as exc:
        logger.warning(
            "No se pudo conectar a la base de datos para inicializar tablas (%s). "
            "El servicio continuará en modo degradado sin persistencia de auditoría.",
            exc,
        )
        return False


def get_db() -> Generator[Optional[Session], None, None]:
    """Generador de sesiones de base de datos con manejo seguro de transacciones.
    
    Si la base de datos no está disponible, captura el error y retorna None,
    permitiendo a los endpoints operar en modo degradado sin latencias de espera.
    """
    if not check_db_connection():
        yield None
        return

    db: Optional[Session] = None
    try:
        db = SessionLocal()
    except Exception as exc:
        logger.warning("Fallo al crear sesión de BD: %s. Operando en modo sin persistencia.", exc)
        yield None
        return

    try:
        yield db
    except Exception:
        if db is not None:
            db.rollback()
        raise
    finally:
        if db is not None:
            db.close()
