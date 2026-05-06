# 03 - Arquitectura del Sistema

## 1. Arquitectura general

SIVECOM usará una arquitectura web modular:

```text
Usuario
  ↓
Frontend React
  ↓
API FastAPI
  ↓
Servicio de procesamiento
  ↓
OCR / Clasificación / Extracción / Validación
  ↓
PostgreSQL + almacenamiento de archivos
  ↓
Dashboard + Reportes
```

## 2. Componentes

### Frontend

Responsable de:

- Login.
- Carga de PDF.
- Dashboard.
- Visualización de páginas.
- Alertas.
- Decisión final.
- Exportación de informe.

### Backend API

Responsable de:

- Recibir archivos.
- Crear expediente.
- Consultar estados.
- Exponer resultados.
- Gestionar usuarios.
- Registrar auditoría.

### Worker de procesamiento

Responsable de:

- Convertir páginas.
- Extraer texto.
- Ejecutar OCR.
- Clasificar documentos.
- Extraer datos.
- Aplicar reglas.

### Base de datos

Responsable de:

- Guardar expedientes.
- Guardar documentos.
- Guardar metadatos extraídos.
- Guardar validaciones.
- Guardar alertas.
- Guardar decisiones y logs.

### Almacenamiento de archivos

Responsable de:

- Guardar PDFs originales.
- Guardar imágenes de páginas.
- Guardar reportes exportados.

## 3. Flujo de procesamiento

1. Usuario sube PDF.
2. Backend guarda archivo.
3. Backend crea expediente en estado `pendiente`.
4. Backend envía tarea al worker.
5. Worker renderiza páginas.
6. Worker extrae texto directo.
7. Worker aplica OCR cuando sea necesario.
8. Worker clasifica páginas.
9. Worker extrae campos.
10. Worker aplica reglas.
11. Worker guarda resultados.
12. Dashboard muestra veredicto.
13. Usuario registra decisión final.

## 4. Decisiones técnicas

### ¿Por qué FastAPI?

- Rápido para APIs.
- Buen soporte de Pydantic.
- Fácil documentación automática.
- Integración natural con Python OCR.

### ¿Por qué PostgreSQL?

- Soporta JSONB.
- Adecuado para auditoría.
- Robusto para sistemas institucionales.

### ¿Por qué motor de reglas?

- Las validaciones administrativas son explícitas.
- Es más explicable que un modelo de IA opaco.
- Permite auditoría.

### ¿Por qué OCR combinado?

- Algunos PDFs tienen texto embebido.
- Otros son escaneados.
- Conviene usar extracción directa primero y OCR como fallback.

## 5. Arquitectura recomendada de carpetas

```text
backend/
  app/
    api/
    core/
    models/
    schemas/
    services/
      pdf_processing/
      ocr/
      classification/
      extraction/
      validation/
      reports/
    workers/
    tests/

frontend/
  src/
    components/
    pages/
    services/
    hooks/
    types/

docs/
skills/
rules/
templates/
```
