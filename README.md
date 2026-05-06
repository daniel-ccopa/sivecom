# SIVECOM - Paquete de planificación y Skills para agentes de IA

**Nombre sugerido:** SIVECOM  
**Significado:** Sistema Inteligente de Verificación de Expedientes de Conformidad Municipal  
**Fecha de creación:** 2026-05-06

Este paquete contiene archivos `.md`, plantillas y reglas para que un agente de IA pueda desarrollar de forma ordenada un sistema web que recibe expedientes PDF de proveedores/servicios, extrae datos clave, valida documentos obligatorios, detecta inconsistencias y genera un veredicto administrativo.

## Qué contiene

- `AGENTS.md`: reglas globales que debe seguir cualquier agente de IA.
- `docs/`: planificación del proyecto, arquitectura, requisitos, base de datos, pruebas, seguridad y despliegue.
- `skills/`: habilidades específicas que el agente puede usar por módulo.
- `templates/`: esquemas y formatos reutilizables.
- `rules/`: reglas iniciales de validación.
- `prompts/`: prompts listos para usar con agentes de programación.
- `backlog/`: tareas ordenadas por fases.

## Cómo usar este paquete con un agente de IA

1. Copia este paquete dentro de la raíz de tu proyecto.
2. Antes de programar, pide al agente:
   > Lee `AGENTS.md`, luego `docs/00_master_plan.md` y `docs/02_prd.md`. Después revisa la skill correspondiente a la tarea.
3. Para cada módulo, usa la skill adecuada:
   - PDF/OCR: `skills/pdf_ocr_extraction/SKILL.md`
   - Clasificación de documentos: `skills/document_classification/SKILL.md`
   - Extracción de datos: `skills/data_extraction_regex/SKILL.md`
   - Validación: `skills/rules_engine_validation/SKILL.md`
   - Backend: `skills/backend_api/SKILL.md`
   - Frontend: `skills/frontend_dashboard/SKILL.md`
   - Base de datos/auditoría: `skills/database_audit/SKILL.md`

## Alcance del MVP

El MVP debe permitir:

1. Cargar un único PDF de expediente.
2. Convertir páginas a texto mediante extracción directa y OCR si es escaneado.
3. Clasificar páginas por tipo de documento.
4. Extraer datos clave.
5. Aplicar validaciones automáticas.
6. Mostrar un dashboard con alertas.
7. Permitir decisión humana final.
8. Exportar informe de revisión.

## Recomendación importante

Este sistema debe apoyar la decisión administrativa, no reemplazarla totalmente. El veredicto automático debe ser tratado como una recomendación auditable.
