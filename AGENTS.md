# AGENTS.md - Instrucciones globales para agentes de IA

## Objetivo general

Desarrollar un sistema web local o intranet para validar expedientes PDF de conformidad de servicios en una municipalidad. El sistema debe recibir un PDF único, extraer información clave, verificar documentos, detectar inconsistencias y presentar un veredicto claro para apoyo administrativo.

## Regla principal

Antes de escribir código, el agente debe leer:

1. `docs/00_master_plan.md`
2. `docs/02_prd.md`
3. `docs/03_architecture.md`
4. La skill correspondiente dentro de `skills/`

## Principios del proyecto

- Priorizar exactitud, trazabilidad y revisión humana.
- No inventar datos que no aparezcan en el expediente.
- Diferenciar entre dato extraído, dato inferido y dato no encontrado.
- Guardar evidencia: página, texto detectado y regla aplicada.
- No exponer datos personales, RUC, firmas o documentos sensibles en logs públicos.
- El sistema debe funcionar con PDFs escaneados y PDFs con texto.
- El sistema debe ser útil aunque el OCR tenga errores.

## Stack tecnológico recomendado

### Backend
- Python 3.11+
- FastAPI
- SQLAlchemy o SQLModel
- Pydantic
- PostgreSQL
- Redis + Celery o RQ para procesamiento en segundo plano
- PyMuPDF / pdfplumber / pdf2image
- OCR: PaddleOCR como motor local principal

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- Shadcn UI opcional
- Axios o TanStack Query

### Base de datos
- PostgreSQL con campos JSONB para metadatos flexibles.

### Despliegue
- Docker Compose para entorno local/intranet.
- Opción futura: servidor Ubuntu con Nginx.

## Reglas de codificación

- Mantener estructura modular.
- Separar extracción, clasificación, validación y presentación.
- No mezclar lógica de negocio con vistas.
- Crear pruebas unitarias para reglas de validación.
- Usar variables de entorno para configuración.
- Nunca colocar credenciales en el repositorio.
- Documentar cada función crítica.
- No eliminar archivos existentes sin autorización.
- Si se modifica una regla, actualizar `rules/validation_rules.md`.

## Manejo de incertidumbre

Cuando el sistema no pueda confirmar algo, debe devolver:

- `estado: "no_encontrado"` si el dato no aparece.
- `estado: "baja_confianza"` si aparece con OCR dudoso.
- `estado: "conflictivo"` si aparece en más de un documento con valores diferentes.
- `estado: "requiere_revision_manual"` si la regla no puede decidir automáticamente.

## Reglas para resultados

Cada resultado de validación debe incluir:

- Tipo de validación.
- Resultado: OK, ADVERTENCIA o ERROR.
- Descripción clara.
- Evidencia textual.
- Página donde se encontró la evidencia.
- Recomendación para el administrativo.

## Comandos sugeridos

Instalar backend:

```bash
pip install -r requirements.txt
```

Ejecutar backend:

```bash
uvicorn app.main:app --reload
```

Ejecutar frontend:

```bash
npm install
npm run dev
```

Ejecutar pruebas:

```bash
pytest
```

Ejecutar con Docker:

```bash
docker compose up --build
```

## Prohibiciones

- No decidir automáticamente pagos reales.
- No reemplazar la firma o revisión del funcionario.
- No entrenar modelos con documentos sensibles sin anonimización.
- No enviar PDFs a servicios externos sin autorización.
- No mostrar RUC/DNI completos si el rol del usuario no lo permite.
