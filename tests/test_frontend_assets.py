"""Pruebas automatizadas de estructura, tokens de diseno y build del Frontend React (HU-07).

Valida la presencia de componentes requeridos, configuracion de Tailwind con la paleta
canonica (#2b2d42, #8d99ae, #edf2f4, #ef233c, #4361ee), regla estricta de cero animaciones,
contratos de endpoints en servicios y artefactos compilados en dist/.
"""

import json
from pathlib import Path
import pytest

WEB_DIR = Path(__file__).resolve().parent.parent / "packages" / "web"


def test_web_package_structure():
    """Verifica que package.json contenga scripts, React 18, Vite, Tailwind y Axios."""
    pkg_file = WEB_DIR / "package.json"
    assert pkg_file.exists(), "web/package.json debe existir"

    with open(pkg_file, "r", encoding="utf-8") as f:
        pkg_data = json.load(f)

    assert pkg_data.get("name") == "sms-sentinel-web"
    scripts = pkg_data.get("scripts", {})
    assert "dev" in scripts and "3090" in scripts["dev"], "El script dev debe apuntar al puerto 3090"
    assert "build" in scripts, "El script build debe existir"

    deps = pkg_data.get("dependencies", {})
    dev_deps = pkg_data.get("devDependencies", {})
    all_deps = {**deps, **dev_deps}

    assert "react" in all_deps
    assert "react-dom" in all_deps
    assert "vite" in all_deps
    assert "tailwindcss" in all_deps
    assert "axios" in all_deps
    assert "lucide-react" in all_deps


def test_tailwind_canonical_palette():
    """Verifica que tailwind.config.js incluya la paleta canonica oficial de DESIGN.md."""
    tailwind_file = WEB_DIR / "tailwind.config.js"
    assert tailwind_file.exists(), "web/tailwind.config.js debe existir"

    content = tailwind_file.read_text(encoding="utf-8")
    canonical_colors = ["#2b2d42", "#8d99ae", "#edf2f4", "#ef233c", "#4361ee"]
    for color in canonical_colors:
        assert color in content, f"El color canonico {color} debe estar configurado en Tailwind"


def test_strict_zero_animation_rule():
    """Verifica que el CSS global aplique la prohibicion estricta de animaciones y transiciones."""
    css_file = WEB_DIR / "src" / "index.css"
    assert css_file.exists(), "web/src/index.css debe existir"

    content = css_file.read_text(encoding="utf-8")
    assert "transition: none !important" in content
    assert "animation: none !important" in content


def test_required_components_exist():
    """Verifica que los componentes de la interfaz modular esten implementados."""
    components_dir = WEB_DIR / "src" / "components"
    assert components_dir.exists()

    required_components = [
        "MessageAnalyzer.tsx",
        "BatchAnalyzer.tsx",
        "NLPStepViewer.tsx",
        "MetricsDashboard.tsx",
        "HistoryAuditTable.tsx",
    ]
    for comp in required_components:
        comp_file = components_dir / comp
        assert comp_file.exists(), f"El componente {comp} debe existir en web/src/components/"


def test_api_service_contract_endpoints():
    """Verifica que el servicio HTTP tipado consuma todos los endpoints de la API."""
    api_service_file = WEB_DIR / "src" / "services" / "api.ts"
    assert api_service_file.exists(), "web/src/services/api.ts debe existir"

    content = api_service_file.read_text(encoding="utf-8")
    assert "/predict" in content
    assert "/predict/batch/csv" in content
    assert "/nlp/debug" in content
    assert "/metrics" in content
    assert "/history" in content
    assert "/health" in content


def test_docker_and_nginx_configuration():
    """Verifica que existan el Dockerfile y configuracion de Nginx para el puerto 3090."""
    dockerfile = WEB_DIR / "Dockerfile"
    nginx_conf = WEB_DIR / "nginx.conf"

    assert dockerfile.exists(), "web/Dockerfile debe existir"
    assert nginx_conf.exists(), "web/nginx.conf debe existir"

    nginx_content = nginx_conf.read_text(encoding="utf-8")
    assert "listen 80" in nginx_content
    assert "try_files $uri $uri/ /index.html" in nginx_content


def test_compiled_dist_artifacts():
    """Verifica que el build de produccion genere el directorio dist con index.html y assets."""
    dist_dir = WEB_DIR / "dist"
    assert dist_dir.exists(), "web/dist debe existir tras la compilacion de produccion"

    index_html = dist_dir / "index.html"
    assert index_html.exists(), "web/dist/index.html debe existir"

    assets_dir = dist_dir / "assets"
    assert assets_dir.exists(), "web/dist/assets debe existir"
    js_files = list(assets_dir.glob("*.js"))
    css_files = list(assets_dir.glob("*.css"))
    assert len(js_files) > 0, "Debe existir al menos un bundle JS generado"
    assert len(css_files) > 0, "Debe existir al menos un bundle CSS generado"


def test_example_resources_and_no_hardcoded_samples():
    """Verifica que los ejemplos residan en resources/example/ y no haya samples hardcodeados en frontend."""
    project_root = Path(__file__).resolve().parent.parent
    example_dir = project_root / "resources" / "example"
    assert example_dir.exists(), "resources/example debe existir"

    samples_json = example_dir / "samples.json"
    batch_csv = example_dir / "batch_samples.csv"
    assert samples_json.exists(), "resources/example/samples.json debe existir"
    assert batch_csv.exists(), "resources/example/batch_samples.csv debe existir"

    with open(samples_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert "samples" in data and len(data["samples"]) > 0
    assert "default_forensic_sample" in data

    csv_text = batch_csv.read_text(encoding="utf-8")
    assert "text\n" in csv_text or "text\r\n" in csv_text
    assert len(csv_text.splitlines()) > 5

    # Validar que los componentes no tengan constantes hardcodeadas de strings de muestra
    batch_analyzer_file = WEB_DIR / "src" / "components" / "BatchAnalyzer.tsx"
    nlp_viewer_file = WEB_DIR / "src" / "components" / "NLPStepViewer.tsx"

    batch_code = batch_analyzer_file.read_text(encoding="utf-8")
    assert "const SAMPLE_CSV_CONTENT" not in batch_code
    assert "@resources/example/batch_samples.csv" in batch_code

    nlp_code = nlp_viewer_file.read_text(encoding="utf-8")
    assert "const DEFAULT_SAMPLE =\n  'ALERTA BANCO" not in nlp_code
    assert "@resources/example/samples.json" in nlp_code
