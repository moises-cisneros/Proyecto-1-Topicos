"""Configuración global de fixtures y rutas para la suite de pruebas de SMS Sentinel."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
_PACKAGES = _ROOT / "packages"

for p in [str(_ROOT), str(_PACKAGES)]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    import pipeline
    import pipeline.nlp
    import pipeline.models
    sys.modules["src"] = pipeline
    sys.modules["src.nlp"] = pipeline.nlp
    sys.modules["src.models"] = pipeline.models
except ImportError:
    pass
