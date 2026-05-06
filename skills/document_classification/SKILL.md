---
name: document-classification
description: Use this skill when classifying pages or segments into document types such as carta, orden de servicio, comprobante, informe, or anexos.
---


# Document Classification Skill

## Purpose

Clasificar páginas del expediente según el tipo de documento administrativo.

## When to use

Usar cuando se necesite:

- Detectar carta de solicitud.
- Detectar orden de servicio.
- Detectar recibo, factura o comprobante.
- Detectar informe de actividades.
- Detectar anexos o fotografías.
- Agrupar páginas consecutivas de un mismo documento.

## Context files

Leer:

- `docs/02_prd.md`
- `docs/05_validation_rules.md`
- `rules/document_keywords.md`

## Classification strategy

Usar reglas por palabras clave inicialmente.

### Carta de solicitud

Palabras clave:

- carta n°
- solicito conformidad
- conformidad del servicio
- señores
- atentamente
- adjunto

### Orden de servicio

Palabras clave:

- orden de servicio
- sistema integrado de gestión administrativa
- siaf
- condiciones generales
- monto total
- proveedor
- afectación presupuestal

### Comprobante

Palabras clave:

- factura electrónica
- recibo por honorarios electrónico
- ruc
- total honorarios
- igv
- total neto recibido
- fecha de emisión

### Informe de actividades

Palabras clave:

- informe n°
- asunto
- referencia
- antecedentes
- análisis
- actividades realizadas
- conclusiones y recomendaciones

### Anexo fotográfico

Palabras clave:

- anexo
- fotografía
- registro fotográfico
- evidencia
- imagen

## Required behavior

El agente debe:

1. Clasificar cada página individualmente.
2. Calcular confianza de clasificación.
3. Agrupar páginas consecutivas.
4. Marcar páginas desconocidas.
5. No forzar clasificación si la confianza es baja.
6. Guardar evidencia textual que justifica la clasificación.

## Output schema

```json
{
  "document_type": "informe_actividades",
  "page_start": 3,
  "page_end": 7,
  "confidence": 0.91,
  "evidence": ["INFORME N°", "ANTECEDENTES", "CONCLUSIONES Y RECOMENDACIONES"]
}
```

## Do

- Usar fuzzy matching.
- Tolerar errores de OCR.
- Guardar por qué se clasificó.
- Permitir reglas configurables.

## Do not

- No clasificar como OK si la confianza es baja.
- No juntar documentos diferentes solo porque son consecutivos.
- No eliminar páginas desconocidas.

## Acceptance checklist

- [ ] Clasifica carta.
- [ ] Clasifica orden de servicio.
- [ ] Clasifica comprobante.
- [ ] Clasifica informe.
- [ ] Detecta páginas en blanco.
- [ ] Devuelve evidencia.
