---
name: backend-api
description: Use this skill when building FastAPI endpoints, services, database models, authentication, and background job orchestration.
---


# Backend API Skill

## Purpose

Guiar el desarrollo del backend FastAPI de SIVECOM.

## When to use

Usar cuando se trabaje en:

- Endpoints.
- Modelos de base de datos.
- Schemas Pydantic.
- Autenticación.
- Subida de archivos.
- Estado de procesamiento.
- Tareas en segundo plano.
- Reportes.

## Context files

Leer:

- `docs/03_architecture.md`
- `docs/04_database_model.md`
- `docs/08_security_privacy.md`

## Required modules

```text
app/
  main.py
  core/
    config.py
    security.py
  api/
    routes_auth.py
    routes_expedientes.py
    routes_documentos.py
    routes_validaciones.py
    routes_reportes.py
  models/
  schemas/
  services/
  workers/
  tests/
```

## Required endpoints

### Auth

- `POST /auth/login`
- `POST /auth/logout`
- `GET /auth/me`

### Expedientes

- `POST /expedientes/upload`
- `GET /expedientes`
- `GET /expedientes/{id}`
- `GET /expedientes/{id}/status`
- `POST /expedientes/{id}/reprocess`

### Validaciones

- `GET /expedientes/{id}/validaciones`
- `GET /expedientes/{id}/alertas`

### Decisión final

- `POST /expedientes/{id}/decision`

### Reportes

- `GET /expedientes/{id}/reporte`

## Required behavior

- Validar archivos.
- Crear expediente antes de procesar.
- Enviar trabajo a cola.
- Devolver estado de procesamiento.
- Guardar logs de auditoría.
- Respetar roles.
- No bloquear la API durante OCR.

## Do

- Usar Pydantic para validación.
- Usar transacciones.
- Manejar errores HTTP claros.
- Crear servicios separados.
- Escribir pruebas.

## Do not

- No procesar OCR pesado en el request principal.
- No guardar contraseñas sin hash.
- No devolver rutas internas absolutas.
- No exponer datos sensibles sin permisos.

## Acceptance checklist

- [ ] Upload funciona.
- [ ] Estado de procesamiento funciona.
- [ ] Resultados se consultan.
- [ ] Decisión final se registra.
- [ ] Auditoría se guarda.
