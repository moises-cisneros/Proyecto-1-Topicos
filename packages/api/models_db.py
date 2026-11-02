"""Modelos ORM de Base de Datos para persistencia y auditoría de inferencias.

Define la entidad MessageAudit para el registro inmutable de consultas evaluadas por
el detector de Spam y Phishing en SMS Sentinel.
"""

from datetime import datetime, timezone
from typing import Any, List

from sqlalchemy import Column, DateTime, Float, Integer, JSON, String, Text, func
from api.database import Base


class MessageAudit(Base):
    """Modelo ORM para la tabla message_audits."""

    __tablename__ = "message_audits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    message_text = Column(String(1000), nullable=False)
    prediction = Column(String(10), nullable=False, index=True)
    probability_spam = Column(Float, nullable=False)
    probability_ham = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    detected_tokens = Column(JSON, nullable=False, default=list)
    latency_ms = Column(Float, nullable=False)

    def to_dict(self) -> dict[str, Any]:
        """Convierte la entidad en un diccionario serializable."""
        return {
            "id": self.id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "message_text": self.message_text,
            "prediction": self.prediction,
            "probability_spam": self.probability_spam,
            "probability_ham": self.probability_ham,
            "risk_level": self.risk_level,
            "detected_tokens": self.detected_tokens or [],
            "latency_ms": self.latency_ms,
        }

