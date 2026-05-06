---
name: pdf-ocr-extraction
description: Use this skill when building or improving PDF ingestion, page rendering, text extraction, and OCR processing.
---


# PDF/OCR Extraction Skill

## Purpose

Guiar al agente cuando trabaje con carga, lectura y procesamiento OCR de expedientes PDF.

## When to use

Usar esta skill cuando la tarea involucre:

- Cargar PDFs.
- Separar páginas.
- Convertir páginas a imágenes.
- Extraer texto directo.
- Aplicar OCR.
- Detectar páginas en blanco.
- Guardar evidencias por página.

## Context files

Leer también:

- `docs/06_pdf_ocr_pipeline.md`
- `docs/03_architecture.md`
- `templates/page_extraction_schema.json`

## Required behavior

El agente debe:

1. Validar que el archivo sea PDF.
2. Guardar el PDF original sin modificar.
3. Obtener número de páginas.
4. Intentar extracción directa de texto.
5. Si el texto es insuficiente, aplicar OCR.
6. Guardar texto original y texto normalizado.
7. Guardar imagen renderizada de cada página.
8. Marcar páginas en blanco.
9. Registrar errores sin detener todo el proceso.
10. Devolver evidencia página por página.

## Suggested implementation

Crear servicios separados:

```text
services/pdf_processing/pdf_reader.py
services/pdf_processing/page_renderer.py
services/ocr/ocr_engine.py
services/ocr/text_normalizer.py
```

## Inputs

- Ruta del PDF.
- ID del expediente.
- Configuración OCR.

## Outputs

Lista de páginas procesadas:

```json
[
  {
    "page_number": 1,
    "text": "...",
    "normalized_text": "...",
    "ocr_used": true,
    "confidence": 81.2,
    "is_blank": false,
    "image_path": "..."
  }
]
```

## Do

- Usar extracción directa antes de OCR.
- Mantener evidencia de cada página.
- Permitir reprocesamiento.
- Manejar PDFs rotados.
- Ser tolerante con mala calidad de escaneo.

## Do not

- No borrar el PDF original.
- No depender solo de OCR.
- No asumir que una página sin texto no tiene contenido.
- No enviar documentos a servicios externos sin autorización.

## Acceptance checklist

- [ ] Procesa PDF con texto.
- [ ] Procesa PDF escaneado.
- [ ] Detecta páginas en blanco.
- [ ] Guarda imagen por página.
- [ ] Guarda texto y confianza.
- [ ] Maneja errores.
