---
name: "Historias de Usuario (HU) / Feature"
about: "Plantilla para especificar una funcionalidad del sistema con criterios de aceptación y calidad"
title: "[HU]: "
labels: ["feature", "user-story"]
assignees: []
---

## 1. Declaración de la Historia de Usuario

* **Como** [tipo de usuario: ej. Analista de Ciberseguridad, Usuario Final, Desarrollador de la API]
* **Quiero** [funcionalidad o capacidad técnica requerida]
* **Para** [beneficio o valor de negocio/técnico que aporta al sistema]

---

## 2. Capas Técnicas Afectadas

- [ ] Capa 1: Datos y EDA (`data/`, `notebooks/`)
- [ ] Capa 2: Pipeline de NLP (`src/nlp/`)
- [ ] Capa 3: Modelado y Serialización ML (`src/models/`, `models/`)
- [ ] Capa 4: Backend REST API & DB (`api/`)
- [ ] Capa 5: Frontend UI & Explicabilidad (`web/`)
- [ ] Capa 6: DevOps, Testing & CI/CD (`.github/`, `scripts/`, `docker/`)

---

## 3. Mapeo de Archivos según la Arquitectura

* **Archivos a Crear:**
  * `ruta/al/archivo.py` - [Propósito técnico del archivo]
* **Archivos a Modificar / Actualizar:**
  * `CONTRIBUCIONES.md` - [Registro de commits y decisiones]

---

## 4. Criterios de Aceptación (Acceptance Criteria)

Definir condiciones verificables en formato *Dado-Cuando-Entonces* o checklist inequívoco:

- [ ] **Escenario 1 (Flujo Principal):**
  - **Dado** [precondición del sistema o datos de entrada]
  - **Cuando** [se ejecuta la acción o inferencia]
  - **Entonces** [resultado esperado observable y medible]
- [ ] **Escenario 2 (Casos de Borde / Errores):**
  - **Dado** [entrada inválida, vacía o atípica]
  - **Cuando** [se procesa la petición]
  - **Entonces** [código HTTP o manejo de excepción adecuado sin caídas del servicio]

---

## 5. Criterios de Calidad y Pruebas Asociadas

- [ ] Pruebas unitarias o de integración implementadas en `tests/`.
- [ ] Cobertura de pruebas validada localmente con `pytest`.
- [ ] Semillas deterministas fijadas (`random_state=42`) si involucra procesamiento o modelos.
- [ ] Tiempos de latencia y uso de memoria dentro de límites aceptables.

---

## 6. Racional Técnico para la Defensa y Trazabilidad

* **Decisión Técnica Adoptada:** [¿Por qué se diseñó e implementó de esta manera?]
* **Alternativa Evaluada y Descartada:** [¿Qué otra alternativa se analizó y por qué razón técnica se rechazó?]
* **Rama Asociada:** `feat/<nombre-funcionalidad>`
