---
name: data-extraction-regex
description: Use this skill when extracting structured fields such as RUC, OS number, amounts, dates, provider name, and service concept.
---


# Data Extraction Regex Skill

## Purpose

Extraer datos clave del texto de cada documento usando expresiones regulares, reglas y fuzzy matching.

## When to use

Usar cuando la tarea involucre:

- RUC.
- Número de orden de servicio.
- Fechas.
- Montos.
- IGV.
- Proveedor.
- Concepto del servicio.
- Número de comprobante.
- Asunto o referencia del informe.

## Context files

Leer:

- `docs/12_data_dictionary.md`
- `templates/extraction_schema.json`
- `rules/field_patterns.md`

## Required behavior

El agente debe:

1. Extraer valores candidatos.
2. Normalizar valores.
3. Calcular confianza.
4. Guardar evidencia textual.
5. Guardar página de origen.
6. Resolver conflictos entre documentos.
7. No inventar datos faltantes.

## Fields to extract

### RUC

- Debe tener 11 dígitos.
- Puede aparecer como `RUC`, `R.U.C.`, `RUC N°`.

### Número de orden de servicio

Patrones posibles:

- `ORDEN DE SERVICIO N° 000000`
- `Orden de Servicio N° 0001582`
- `O/S 0001582`
- `OS N° 0001582`

### Montos

Tipos:

- Subtotal.
- IGV.
- Total.
- Total honorarios.
- Total neto recibido.
- Monto de cuota.

### Fechas

Formatos posibles:

- `07 de mayo de 2025`
- `07/05/2025`
- `09-04-2025`
- `Puno, 07 de Mayo del 2025`

### Proveedor

Puede aparecer cerca de:

- `Proveedor:`
- `Recibí de:`
- `Datos del proveedor`
- `Nombre/Razón Social`

## Output schema

```json
{
  "field": "numero_os",
  "value": "0001582",
  "normalized_value": "0001582",
  "confidence": 0.95,
  "page": 11,
  "document_type": "orden_servicio",
  "evidence": "ORDEN DE SERVICIO N° 0001582",
  "method": "regex",
  "status": "encontrado"
}
```

## Conflict resolution

Si un campo aparece con valores diferentes:

1. Guardar todos los candidatos.
2. Priorizar documento fuente más confiable.
3. Marcar conflicto si no hay coincidencia.
4. Enviar a validación manual.

## Do

- Normalizar montos a decimal.
- Normalizar fechas a ISO `YYYY-MM-DD`.
- Conservar valor original.
- Registrar página y evidencia.
- Usar tolerancia a errores de OCR.

## Do not

- No asumir RUC por nombre.
- No completar montos faltantes con cálculos si no hay evidencia.
- No ocultar conflictos.
- No sobreescribir valores originales.

## Acceptance checklist

- [ ] Extrae RUC.
- [ ] Extrae número de O/S.
- [ ] Extrae fechas.
- [ ] Extrae montos.
- [ ] Extrae proveedor.
- [ ] Guarda evidencia.
- [ ] Detecta conflictos.
