---
name: database-audit
description: Use this skill when designing database models, migrations, audit logs, history, and traceability.
---


# Database and Audit Skill

## Purpose

Garantizar que todos los datos del expediente sean guardados con trazabilidad.

## When to use

Usar cuando se trabaje en:

- Modelos SQL.
- Migraciones.
- Auditoría.
- Historial.
- Logs.
- Decisiones.
- Búsqueda y filtros.

## Context files

Leer:

- `docs/04_database_model.md`
- `docs/08_security_privacy.md`
- `docs/12_data_dictionary.md`

## Required behavior

El agente debe:

1. Crear modelos normalizados.
2. Usar JSONB para metadatos flexibles.
3. Guardar evidencia de campos extraídos.
4. Guardar cada validación.
5. Guardar cada alerta.
6. Guardar decisión final.
7. Guardar auditoría de acciones críticas.

## Actions to audit

- Login.
- Carga de expediente.
- Reprocesamiento.
- Cambio de estado.
- Decisión final.
- Exportación de informe.
- Cambio de reglas.
- Eliminación o desactivación.

## Do

- Usar migraciones.
- Crear índices para búsquedas frecuentes.
- Guardar timestamps.
- Relacionar usuario con acciones.
- Evitar borrado físico cuando sea posible.

## Do not

- No guardar contraseñas planas.
- No borrar expedientes sin rastro.
- No guardar información sensible en logs planos.
- No mezclar metadatos críticos solo en JSON si deben buscarse mucho.

## Acceptance checklist

- [ ] Migraciones listas.
- [ ] Tablas principales creadas.
- [ ] Logs de auditoría.
- [ ] Índices básicos.
- [ ] Decisiones guardadas.
