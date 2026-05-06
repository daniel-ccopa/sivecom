---
name: frontend-dashboard
description: Use this skill when creating the React dashboard, upload flow, evidence viewer, validations table, and final decision UI.
---


# Frontend Dashboard Skill

## Purpose

Construir una interfaz clara para revisar expedientes procesados.

## When to use

Usar cuando se trabaje en:

- Bandeja de expedientes.
- Carga de PDF.
- Dashboard de resultados.
- Checklist.
- Alertas.
- Visualización de páginas.
- Decisión final.
- Exportación.

## Context files

Leer:

- `docs/07_ui_ux_dashboard.md`
- `docs/02_prd.md`

## Required pages

```text
/pages/Login.tsx
/pages/ExpedientesList.tsx
/pages/ExpedienteUpload.tsx
/pages/ExpedienteDetail.tsx
/pages/Settings.tsx
```

## Required components

```text
/components/StatusBadge.tsx
/components/VerdictCard.tsx
/components/ChecklistTable.tsx
/components/AlertsTable.tsx
/components/ExtractedFieldsTable.tsx
/components/PageViewer.tsx
/components/EvidencePanel.tsx
/components/DecisionModal.tsx
```

## UX rules

- Mostrar resumen primero.
- Mostrar alertas por severidad.
- Hacer fácil encontrar la página de evidencia.
- Pedir observación cuando se cambia el veredicto sugerido.
- No saturar con datos técnicos.
- Usar lenguaje administrativo claro.

## States

- Pendiente.
- Procesando.
- Procesado.
- Con alertas.
- Aprobado.
- Rechazado.
- Revisión manual.
- Error.

## Do

- Usar TypeScript.
- Crear tipos compartidos.
- Manejar loading y errores.
- Usar paginación.
- Crear filtros.
- Mostrar evidencias.

## Do not

- No mostrar datos sensibles innecesarios.
- No permitir aprobar si no hay rol suficiente.
- No ocultar alertas.
- No hacer decisiones irreversibles sin confirmación.

## Acceptance checklist

- [ ] Permite subir PDF.
- [ ] Muestra progreso.
- [ ] Muestra veredicto.
- [ ] Muestra checklist.
- [ ] Muestra alertas.
- [ ] Permite decisión final.
