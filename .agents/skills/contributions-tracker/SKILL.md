---
name: contributions-tracker
description: >-
  Provides standards, template schema, and verification procedures for tracking commits
  and technical design decisions in CONTRIBUCIONES.md, avoiding recursion paradoxes
  and maintaining 100% alignment with git log.
---

# Contributions Tracker & Audit Verification

Use this skill whenever opening a Pull Request, finishing a feature branch, or registering code changes in `CONTRIBUCIONES.md`.

## 1. El Principio de Granularidad por Historia de Usuario (HU)

### La Paradoja del Commit Recursivo (Por qué NO commitear tras cada commit)
En Git, el hash de un commit es un digest criptográfico inmutable de su contenido. Un commit no puede contener su propio hash. Intentar registrar el commit anterior en el commit siguiente genera una cadena infinita donde el 50% del historial se vuelve ruido administrativo y el último commit del proyecto (`tag: entrega-final`) jamás podría registrarse.

### La Regla de Oro
Las contribuciones se registran **por Unidad de Funcionalidad / Historia de Usuario (HU)** al finalizar el desarrollo de la rama antes del Pull Request:
1. Desarrollar la funcionalidad en la rama `feat/huXX-...` con commits atómicos granulares.
2. Al finalizar los cambios de código y pruebas, ejecutar `git log --oneline -n <N>` en la rama para obtener los hashes.
3. Actualizar `CONTRIBUCIONES.md` en la **Tabla 2.2**, documentando el hash clave de la funcionalidad, la issue vinculada, la descripción técnica y la alternativa descartada.
4. Realizar el último commit de la rama: `docs(contribuciones): registrar entregable de huXX`.
5. Abrir el Pull Request hacia `main`. Al mergear, `CONTRIBUCIONES.md` ya contiene los hashes exactos de la funcionalidad.

---

## 2. Esquema Obligatorio de Registro (Plantilla de Fila)

Cada fila insertada en la tabla debe cumplir estrictamente con este formato:

```markdown
| `hash_corto` | `feat/huXX-nombre` | #X | `tipo(modulo)` | Descripción técnica concisa | **Decisión:** Razón técnica por la que se diseñó e implementó de esta forma. **Alternativa descartada:** Qué otra opción se evaluó y por qué motivo se rechazó. |
```

### Reglas de Calidad del Contenido
* **Hash Real:** El hash debe existir en el historial de Git (`git log`). Prohibido dejar `*[Hash]*` o `TBD`.
* **Cero Ambigüedad:** Prohibido descripciones genéricas como *"arreglar cosas"* o *"se hizo porque era mejor"*.
* **Estructura de Decisión Obligatoria:** Toda fila debe incluir las etiquetas `**Decisión:**` y `**Alternativa descartada:**` para blindar la justificación técnica ante preguntas de auditoría.

---

## 3. Procedimiento de Verificación Automatizada

Antes de commitear o integrar una rama:
1. Ejecutar el script de auditoría:
   ```bash
   python scripts/verify_contributions.py
   ```
2. El script verifica:
   * Que todas las columnas requeridas existan.
   * Que no existan placeholders pendientes.
   * Que los hashes declarados pertenezcan al repositorio (`git log`).
   * Que cada fila contenga la decisión y alternativa descartada.
3. Si el script falla con código de salida 1, corregir las filas observadas antes de hacer push.
