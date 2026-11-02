"""Módulo de configuración y conexión a Base de Datos PostgreSQL con SQLAlchemy.

Configurado para operar en el puerto 5439 (local en Windows/Host) o 5432 (red Docker),
con connection pooling resiliente y degradación elegante si la base de datos no está disponible.
"""

import logging
import os
import time
from typing import Generator, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger("sms_sentinel.database")

# Configuración de URL de conexión por defecto
# Puerto 5439 asignado específicamente para evitar colisiones con PostgreSQL local del host (5432)
DEFAULT_POSTGRES_URL = "postgresql://postgres:postgres@localhost:5439/sms_sentinel_db"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_POSTGRES_URL)

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
        "connect_args": {"connect_timeout": 1},
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


def check_db_connection(force: bool = False) -> bool:
    """Verifica si la base de datos está accesible y responde a consultas.
    
    Implementa un caché de 5 segundos para evitar sobrecarga de sondeo y latencias
    cuando el servidor de base de datos se encuentra inaccesible.
    """
    global _last_check_time, _last_check_status
    now = time.monotonic()
    if not force and (now - _last_check_time < 5.0):
        return _last_check_status

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        _last_check_status = True
    except Exception as exc:
        logger.debug("Comprobación de conexión a BD fallida: %s", exc)
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
            "Base de datos no disponible al iniciar. Las tablas se crearán automáticamente al reconectar."
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
        yield db
    except Exception as exc:
        logger.warning("Fallo al obtener sesión de BD: %s. Operando en modo sin persistencia.", exc)
        if db is not None:
            db.rollback()
        yield None
    finally:
        if db is not None:
            db.close()
