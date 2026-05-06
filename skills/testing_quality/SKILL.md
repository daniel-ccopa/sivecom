---
name: testing-quality
description: Use this skill when writing tests, validating extraction accuracy, checking rules, and preparing quality reports.
---


# Testing and Quality Skill

## Purpose

Asegurar que el sistema sea confiable antes de usarlo con expedientes reales.

## When to use

Usar cuando se trabaje en:

- Pruebas unitarias.
- Pruebas de integración.
- Dataset de prueba.
- Medición de precisión.
- Validación de reglas.
- QA del dashboard.

## Context files

Leer:

- `docs/09_testing_plan.md`
- `rules/validation_rules.md`

## Required tests

### Extracción

- RUC correcto.
- RUC con puntos y espacios.
- Monto con S/.
- Monto con coma decimal.
- Fecha en texto.
- Fecha numérica.
- Número de O/S.

### Clasificación

- Carta.
- Orden de servicio.
- Informe.
- Comprobante.
- Página desconocida.
- Página en blanco.

### Validaciones

- Faltan documentos.
- Montos coinciden.
- Monto excede O/S.
- IGV correcto.
- RUC no coincide.
- Fecha incoherente.
- Expediente duplicado.

## Test data

Usar documentos anonimizados. Nunca subir datos reales sensibles a repositorios públicos.

## Do

- Crear fixtures.
- Probar reglas individualmente.
- Probar pipeline completo.
- Medir precisión.
- Documentar errores conocidos.

## Do not

- No usar PDFs reales no anonimizados en GitHub.
- No aprobar sin pruebas de reglas críticas.
- No ignorar errores de OCR.

## Acceptance checklist

- [ ] Pruebas unitarias.
- [ ] Pruebas de integración.
- [ ] Datos de prueba anonimizados.
- [ ] Reporte de precisión.
- [ ] Casos negativos probados.
