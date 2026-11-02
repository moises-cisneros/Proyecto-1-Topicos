# Guía de Contribución y Buenas Prácticas de Git (CONTRIBUTING.md)

Este documento define el flujo de trabajo y las normas de control de versiones requeridas para el desarrollo del proyecto **SMS Sentinel**.

## 1. Reglas Fundamentales del Repositorio

* **Autoría Individual:** Todo commit debe reflejar el nombre y correo del autor registrado en Git.
* **Prohibición de Atribuciones IA:** No utilizar etiquetas `Co-authored-by` asociadas a asistentes artificiales.
* **Historial Limpio:** No realizar *force push* (`git push --force`) ni reescritura destructiva de la rama principal (`squash` masivo) para mantener un historial de cambios granular, auditable y trazable.

## 2. Formato de Mensajes de Commit (Conventional Commits)

Se exige el uso estricto del estándar Conventional Commits:

```text
<tipo>(<alcance opcional>): <descripción concisa en imperativo y minúsculas>

[cuerpo opcional detallando el porqué y las alternativas consideradas]
```

### Tipos Permitidos

* `feat`: Nueva funcionalidad (ej. `feat(nlp): implementar normalizador con tokens semanticos`).
* `fix`: Corrección de un fallo (ej. `fix(api): validar texto vacio en endpoint predict`).
* `docs`: Cambios exclusivamente en documentación (ej. `docs: actualizar informe con matriz de confusion`).
* `test`: Adición o refactorización de pruebas (ej. `test(pipeline): anadir pruebas unitarias de tokenizacion`).
* `refactor`: Cambio de código que no añade features ni corrige bugs (ej. `refactor(models): modularizar gridsearch`).
* `chore`: Mantenimiento, dependencias o configuración Docker (ej. `chore(docker): mapear puerto postgres a 5439`).

## 3. Estrategia de Ramas

* `main`: Rama de producción estable. Contiene las versiones estables y liberaciones del sistema.
* `feat/<nombre-funcionalidad>`: Rama para el desarrollo de módulos (ej. `feat/hu01-data-eda`, `feat/hu02-nlp-pipeline`).
* Se integra a `main` mediante Pull Request tras verificar las pruebas automatizadas del pipeline de CI.
