# 13 - Prompts para usar con agentes de IA

## Prompt inicial del proyecto

```text
Lee AGENTS.md y toda la carpeta docs/. Luego resume el proyecto en 10 puntos y propón la estructura inicial de carpetas para backend y frontend. No escribas código todavía.
```

## Prompt para backend

```text
Lee AGENTS.md, docs/03_architecture.md y skills/backend_api/SKILL.md. Crea la estructura inicial del backend FastAPI con módulos separados para expedientes, documentos, validaciones y usuarios.
```

## Prompt para PDF/OCR

```text
Lee skills/pdf_ocr_extraction/SKILL.md y docs/06_pdf_ocr_pipeline.md. Implementa un servicio que reciba un PDF, genere páginas como imágenes, extraiga texto directo y use OCR si no encuentra texto suficiente.
```

## Prompt para clasificación documental

```text
Lee skills/document_classification/SKILL.md. Crea un clasificador basado en reglas y palabras clave para identificar carta, orden de servicio, comprobante, informe y anexos.
```

## Prompt para validaciones

```text
Lee skills/rules_engine_validation/SKILL.md y rules/validation_rules.md. Implementa un motor de reglas explicable que devuelva OK, WARNING o ERROR con evidencia.
```

## Prompt para frontend

```text
Lee skills/frontend_dashboard/SKILL.md y docs/07_ui_ux_dashboard.md. Crea el dashboard de expedientes con bandeja, vista de detalle, alertas, checklist y botón de decisión final.
```

## Prompt para pruebas

```text
Lee skills/testing_quality/SKILL.md y docs/09_testing_plan.md. Crea pruebas unitarias para extracción de RUC, montos, fechas, IGV y reglas de validación.
```
