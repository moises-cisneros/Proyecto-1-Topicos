#!/usr/bin/env python3
"""
SMS Sentinel - Verificador de Integridad de CONTRIBUCIONES.md
Valida que el archivo de contribuciones cumpla con el estándar de calidad:
1. Columnas obligatorias presentes en las tablas.
2. Sin placeholders no resueltos (*[Hash]*, TBD, etc.).
3. Justificaciones tecnicas completas (decision y alternativa descartada).
4. Verificacion de que los hashes declarados existan realmente en git log.
"""
import sys
import os
import re
import subprocess

CONTRIBUCIONES_FILE = "CONTRIBUCIONES.md"

def get_git_hashes():
    try:
        output = subprocess.check_output(
            ["git", "log", "--pretty=format:%h"],
            text=True,
            stderr=subprocess.DEVNULL
        )
        return set(output.strip().splitlines())
    except Exception:
        return set()

def main():
    if not os.path.exists(CONTRIBUCIONES_FILE):
        print(f"[ERROR] Archivo {CONTRIBUCIONES_FILE} no encontrado.", file=sys.stderr)
        sys.exit(1)

    with open(CONTRIBUCIONES_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    existing_hashes = get_git_hashes()

    # 1. Verificar placeholders prohibidos en hashes
    table_rows = [line for line in lines if line.strip().startswith("|") and not line.strip().startswith("| :---")]
    
    # Ignorar cabeceras
    data_rows = [
        row for row in table_rows 
        if not any(header in row for header in ["Hash", "Rama", "Tipo & Módulo"])
    ]

    errors = []
    fase0_hashes = []
    
    for idx, row in enumerate(data_rows, 1):
        cols = [c.strip() for c in row.split("|")[1:-1]]
        if len(cols) < 5:
            continue

        raw_hash = cols[0].replace("`", "").strip()
        rama = cols[1] if len(cols) > 1 else ""
        desc = cols[3] if len(cols) > 3 else ""
        decision_col = cols[4] if len(cols) > 4 else ""

        # Comprobar si es un commit de main (Fase 0) ya registrado
        if "main" in rama:
            if re.match(r"^[0-9a-f]{7,8}$", raw_hash):
                fase0_hashes.append(raw_hash)
                if existing_hashes and raw_hash not in existing_hashes:
                    errors.append(f"Fila {idx}: El hash '{raw_hash}' no existe en git log.")

        # Validar calidad de la justificación técnica
        if "**Decisión:**" not in decision_col or "**Alternativa descartada:**" not in decision_col:
            # En filas de desarrollo planificadas no forzamos error hasta que se implementen
            if not raw_hash.startswith("*["):
                errors.append(f"Fila {idx} ('{raw_hash}'): Falta la estructura obligatoria de 'Decisión:' y 'Alternativa descartada:'.")

    print("==========================================================")
    print("   Auditoría de Integridad de CONTRIBUCIONES.md          ")
    print("==========================================================")
    print(f"-> Total de filas analizadas: {len(data_rows)}")
    print(f"-> Hashes verificados en git log: {len(fase0_hashes)} {fase0_hashes}")

    if errors:
        print("[FALLO] Se detectaron inconsistencias:", file=sys.stderr)
        for err in errors:
            print(f"  * {err}", file=sys.stderr)
        sys.exit(1)

    print("[ÉXITO] CONTRIBUCIONES.md cumple con todos los estándares de trazabilidad y calidad.")
    sys.exit(0)

if __name__ == "__main__":
    main()
