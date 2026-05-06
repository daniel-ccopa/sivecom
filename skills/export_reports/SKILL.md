---
name: export-reports
description: Use this skill when generating HTML/PDF reports for administrative review, conformity support, or audit evidence.
---


# Export Reports Skill

## Purpose

Generar informes claros y auditables sobre la revisión del expediente.

## When to use

Usar cuando se necesite:

- Crear informe de revisión.
- Exportar PDF.
- Exportar HTML.
- Resumir alertas.
- Incluir evidencia.

## Context files

Leer:

- `templates/report_template.md`
- `docs/07_ui_ux_dashboard.md`
- `docs/05_validation_rules.md`

## Required report sections

1. Datos del expediente.
2. Datos del proveedor.
3. Orden de servicio.
4. Documentos encontrados.
5. Checklist.
6. Datos extraídos.
7. Validaciones.
8. Alertas.
9. Evidencia.
10. Veredicto sugerido.
11. Decisión final.
12. Usuario responsable.
13. Fecha de emisión.

## Required behavior

- No incluir datos sensibles innecesarios.
- Incluir advertencia de que es apoyo administrativo.
- Incluir evidencia por página.
- Incluir observación de usuario.
- Registrar exportación en auditoría.

## Do

- Usar plantilla HTML.
- Generar PDF desde HTML.
- Mostrar tabla de alertas.
- Enmascarar datos si el rol lo exige.

## Do not

- No inventar conclusiones.
- No ocultar alertas.
- No presentar veredicto automático como decisión legal definitiva.

## Acceptance checklist

- [ ] Genera reporte.
- [ ] Incluye veredicto.
- [ ] Incluye evidencias.
- [ ] Incluye decisión final.
- [ ] Guarda log de exportación.
