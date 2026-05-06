---
name: rules-engine-validation
description: Use this skill when implementing the validation engine that checks documents, amounts, dates, duplicated records, and consistency.
---


# Rules Engine Validation Skill

## Purpose

Implementar un motor de reglas explicable para evaluar expedientes y generar alertas.

## When to use

Usar cuando la tarea involucre:

- Checklist documental.
- Validación de montos.
- Validación de IGV.
- Comparación de RUC.
- Comparación de número de O/S.
- Validación de fechas.
- Detección de duplicados.
- Veredicto sugerido.

## Context files

Leer:

- `docs/05_validation_rules.md`
- `rules/validation_rules.md`
- `templates/validation_result_schema.json`

## Required behavior

Cada regla debe devolver:

- `rule_id`
- `status`: OK, WARNING, ERROR, CRITICAL.
- `passed`: true/false.
- `message`.
- `evidence`.
- `recommendation`.
- `affected_fields`.

## Rule categories

### Checklist

Verifica presencia de documentos obligatorios.

### Consistency

Compara campos entre documentos.

### Financial

Valida montos, subtotal, IGV y total.

### Temporal

Valida fechas y orden cronológico.

### Duplicate

Busca repetición de expediente, O/S o comprobante.

### Semantic

Verifica que el informe guarde relación con el servicio.

## Verdict logic

```text
Si hay CRITICAL o ERROR grave → rechazar
Si hay WARNING importante → revision_manual
Si hay datos no encontrados → revision_manual
Si todo está OK → procede_conformidad
```

## Suggested implementation

Crear una clase base:

```python
class ValidationRule:
    rule_id: str
    name: str
    severity: str

    def evaluate(self, context):
        ...
```

Y reglas concretas:

```text
RequiredDocumentsRule
OSNumberConsistencyRule
RUCConsistencyRule
AmountConsistencyRule
IGVCalculationRule
DateCoherenceRule
DuplicateFileRule
ReportCoherenceRule
SignaturePresenceRule
```

## Do

- Hacer reglas unit-testables.
- Mantener reglas configurables.
- Generar evidencia.
- Ser conservador ante duda.
- Priorizar revisión manual si falta confianza.

## Do not

- No aprobar automáticamente si hay datos faltantes.
- No ocultar advertencias.
- No mezclar extracción con validación.
- No decidir pago real.

## Acceptance checklist

- [ ] Ejecuta reglas por expediente.
- [ ] Devuelve estado por regla.
- [ ] Genera veredicto.
- [ ] Guarda evidencias.
- [ ] Tiene pruebas unitarias.
