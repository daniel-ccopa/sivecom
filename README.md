# SIVECOM

Sistema Inteligente de Verificacion de Expedientes de Conformidad Municipal.

Esta version cubre las fases iniciales del proyecto:

- Fase 1: backend FastAPI, configuracion por entorno, PostgreSQL en Docker Compose y prueba de salud.
- Fase 2: carga segura de expedientes PDF y registro local de metadatos basicos.
- Fase 3: extraccion de texto embebido desde PDFs digitales.
- Fase 4: OCR local con PaddleOCR para paginas sin texto digital extraible.
- Fase 5: segmentacion de documentos por reglas de palabras clave y patrones.
- Fase 6: extraccion de datos clave con regex y normalizacion.
- Fase 7: motor de reglas de validacion con evidencias y veredicto sugerido.
- Fase 8: dashboard administrativo simple para revisar expedientes.

## Estructura

```text
backend/
  app/
    api/
      router.py
      routes_expedientes.py
    core/
      config.py
    models/
      document_segment.py
      extracted_data.py
      expediente.py
      text_extraction.py
      validation_result.py
    schemas/
      document_segments.py
      extracted_data.py
      expedientes.py
      text_extraction.py
      validation_result.py
    services/
      data_extraction/
      document_segmentation/
      expedientes/
      ocr/
      pdf_processing/
      storage/
      validation/
    main.py
  tests/
    test_expedientes_upload.py
    test_document_segmenter.py
    test_field_extractor.py
    test_health.py
    test_pdf_text_extractor.py
    test_validation_engine.py
  Dockerfile
  pytest.ini
  requirements.txt
frontend/
  src/
    components/
    pages/
    services/
    utils/
    App.tsx
    main.tsx
    styles.css
  Dockerfile
  package.json
  vite.config.ts
docker-compose.yml
.env.example
storage/
  data_extractions/
  metadata/
  segmentations/
  text_extractions/
  uploads/
  validations/
```

## Requisitos

- Python 3.11+
- Node.js 22+
- Docker y Docker Compose

## Configuracion

Copiar variables de entorno:

```bash
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Variables OCR disponibles:

- `OCR_LANGUAGE`: idioma para PaddleOCR, por defecto `es`.
- `OCR_DPI`: resolucion usada para renderizar paginas sin texto digital, por defecto `200`.
- `PADDLE_OCR_BASE_DIR`: carpeta local donde PaddleOCR guarda sus modelos, por defecto `storage/paddleocr_models`.
- `PADDLE_USE_GPU`: usar GPU si el entorno tiene PaddlePaddle GPU compatible, por defecto `false`.
- `PADDLE_USE_TEXTLINE_ORIENTATION`: activar correccion de orientacion de lineas, por defecto `false` para acelerar PDFs municipales escaneados en posicion normal.
- `DISABLE_MODEL_SOURCE_CHECK`: evita comprobaciones de conectividad del proveedor de modelos, usar `True`.

En ejecucion local, PaddleOCR funciona de forma local. La primera ejecucion puede descargar modelos OCR a `PADDLE_OCR_BASE_DIR`; los PDFs no se envian a servicios externos.

Configurar frontend:

```bash
cd frontend
cp .env.example .env
```

En Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Por defecto `frontend/.env` deja `VITE_API_BASE_URL=` vacio. Asi el dashboard llama a la API usando el mismo host con el que abres la web:

- `http://localhost:5173` llama a `http://localhost:8000`.
- `http://192.168.0.123:5173` llama a `http://192.168.0.123:8000`.

Para red local, confirma en `.env` que `CORS_ORIGINS` incluya la IP Wi-Fi actual, por ejemplo `http://192.168.0.123:5173`, o que `CORS_ORIGIN_REGEX` permita el rango `192.168.x.x`.

## Ejecutar Backend Local

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Importante para intranet: no ejecutes el backend solo con `uvicorn app.main:app --reload`, porque Uvicorn queda escuchando en `127.0.0.1` y solo funciona en tu propia PC.

Si usas CPU, `requirements.txt` instala `paddlepaddle` desde el indice oficial de PaddlePaddle y `paddleocr` desde PyPI. Si deseas usar GPU, instala la variante `paddlepaddle-gpu` adecuada para tu CUDA segun la documentacion oficial y deja `PADDLE_USE_GPU=true`.

API:

- `GET /health`
- `GET /expedientes`
- `GET /expedientes/{id}/datos`
- `GET /expedientes/{id}/pdf`
- `POST /expedientes/upload`
- `GET /expedientes/{id}`
- `GET /expedientes/{id}/alertas`
- `POST /expedientes/{id}/reprocess`
- `GET /expedientes/{id}/segmentos`
- `GET /expedientes/{id}/texto`
- `GET /expedientes/{id}/validaciones`

Respuesta esperada:

```json
{
  "status": "ok",
  "service": "SIVECOM API"
}
```

## Probar carga de PDF

Con el backend activo:

```bash
curl -X POST "http://localhost:8000/expedientes/upload" \
  -F "file=@ruta/al/expediente.pdf;type=application/pdf"
```

Respuesta esperada:

```json
{
  "id": 1,
  "codigo_interno": "SIV-000001",
  "archivo_original": "expediente.pdf",
  "tamano_bytes": 12345,
  "fecha_carga": "2026-05-06T00:00:00Z",
  "estado": "pendiente"
}
```

El PDF se guarda con un nombre interno no predecible en `storage/uploads/`.
Los metadatos basicos se registran en `storage/metadata/expedientes.json`.
No se devuelve la ruta interna del archivo.
La respuesta de carga se devuelve apenas el archivo queda guardado; la extraccion OCR y validacion continuan en segundo plano.

Para visualizar el PDF almacenado en la aplicacion:

```bash
curl "http://localhost:8000/expedientes/1/pdf"
```

Al cargar un PDF se intenta extraer texto digital embebido por pagina.
Si una pagina no tiene texto digital, se renderiza en memoria y se aplica OCR local. No se guarda ni expone la imagen renderizada.

## Consultar texto extraido

```bash
curl "http://localhost:8000/expedientes/1/texto"
```

Respuesta esperada para un PDF digital con texto:

```json
{
  "expediente_id": 1,
  "status": "extraido",
  "total_pages": 1,
  "total_char_count": 23,
  "extracted_at": "2026-05-06T00:00:00Z",
  "pages": [
    {
      "page_number": 1,
      "text": "Texto digital de prueba",
      "char_count": 23,
      "extraction_method": "direct_text",
      "ocr_used": false,
      "ocr_confidence": null,
      "error": null
    }
  ],
  "error": null
}
```

Si el texto proviene de OCR, la pagina queda marcada asi:

```json
{
  "status": "extraido_con_ocr",
  "pages": [
    {
      "page_number": 1,
      "text": "Texto detectado por OCR",
      "char_count": 23,
      "extraction_method": "ocr",
      "ocr_used": true,
      "ocr_confidence": 86.0,
      "error": null
    }
  ],
  "error": null
}
```

Si una pagina no tiene texto digital y OCR no detecta texto:

```json
{
  "status": "sin_texto_extraible",
  "error": "No se encontro texto extraible en el PDF."
}
```

Si el motor OCR local no esta disponible:

```json
{
  "status": "error_ocr",
  "error": "No se pudo extraer texto de las paginas sin texto digital."
}
```

Los resultados se guardan en `storage/text_extractions/`.

## Consultar segmentos documentales

Despues de cargar un expediente, el sistema clasifica paginas y agrupa paginas consecutivas del mismo tipo documental.

```bash
curl "http://localhost:8000/expedientes/1/segmentos"
```

Respuesta esperada:

```json
{
  "expediente_id": 1,
  "status": "segmentado",
  "segmented_at": "2026-05-06T00:00:00Z",
  "segments": [
    {
      "document_type": "orden_servicio",
      "page_start": 2,
      "page_end": 3,
      "text": "ORDEN DE SERVICIO ...",
      "confidence": 0.72,
      "evidence": ["orden de servicio", "datos del proveedor", "monto total"]
    }
  ]
}
```

Tipos documentales iniciales:

- `carta_solicitud`
- `orden_servicio`
- `recibo_honorarios`
- `factura`
- `informe_actividades`
- `anexo_fotografico`
- `desconocido`

Los segmentos se guardan localmente en `storage/segmentations/`.

Si una carta contiene claramente `informe de actividades` y el detalle de actividades/labores, el sistema registra tambien un segmento `informe_actividades` embebido en esa misma pagina. Esto ayuda a no rechazar expedientes donde carta e informe vienen integrados en un solo documento.

## Consultar datos clave extraidos

Despues de segmentar el expediente, el sistema aplica expresiones regulares y normalizadores para extraer campos clave.

```bash
curl "http://localhost:8000/expedientes/1/datos"
```

Campos actuales:

- `proveedor`
- `ruc`
- `numero_orden_servicio`
- `monto_total_os`
- `monto_entregable`
- `concepto`
- `descripcion_servicio`
- `numero_entregables`
- `porcentaje_entregable`

Respuesta esperada:

```json
{
  "expediente_id": 1,
  "status": "extraido",
  "extracted_at": "2026-05-06T00:00:00Z",
  "fields": [
    {
      "field": "ruc",
      "value": "20*******67",
      "normalized_value": "20*******67",
      "source": "orden_servicio",
      "page": 2,
      "confidence": 0.95,
      "evidence": "RUC: 20*******67",
      "method": "regex"
    }
  ]
}
```

Cada dato extraido conserva valor, fuente documental, pagina y confianza. Los resultados se guardan localmente en `storage/data_extractions/`.

## Consultar validaciones

Despues de extraer datos clave, el sistema ejecuta reglas conservadoras y genera un veredicto sugerido.

```bash
curl "http://localhost:8000/expedientes/1/validaciones"
```

Validaciones iniciales:

- Checklist de documentos obligatorios: carta, orden de servicio, informe y comprobante de pago (recibo por honorarios o factura).
- Presencia de datos principales solicitados.
- Coincidencia de numero de orden de servicio.
- Coincidencia de RUC.
- Revision de monto total de O/S y monto de entregable.
- Revision de cronograma de entregables: cantidad, porcentajes y monto esperado por entregable.
- Presencia de concepto y descripcion del servicio.
- Coincidencia de proveedor.
- Coherencia textual del servicio entre documentos.

Respuesta esperada:

```json
{
  "expediente_id": 1,
  "verdict": "procede_conformidad",
  "summary": {
    "ok": 9,
    "advertencias": 0,
    "errores": 0,
    "criticas": 0
  },
  "validations": [
    {
      "rule_id": "R001",
      "tipo": "campos_principales_detectados",
      "resultado": "OK",
      "severidad": "info",
      "mensaje": "Los datos principales solicitados fueron detectados.",
      "evidencia": [
        {
          "text": "ORDEN DE SERVICIO N 0001582",
          "page": 2,
          "document_type": "orden_servicio",
          "field": "numero_orden_servicio"
        }
      ],
      "recomendacion": "Continuar con la revision administrativa.",
      "passed": true,
      "affected_fields": [
        "numero_orden_servicio",
        "ruc",
        "proveedor",
        "monto_total_os",
        "monto_entregable",
        "concepto",
        "descripcion_servicio"
      ]
    }
  ],
  "validated_at": "2026-05-06T00:00:00Z"
}
```

Los resultados se guardan localmente en `storage/validations/`. Las evidencias textuales se recortan y los RUC de 11 digitos se enmascaran en esta salida de validacion.

## Ejecutar Dashboard

Con el backend activo:

```bash
cd frontend
npm install
npm run dev
```

Abrir:

```text
http://localhost:5173
```

En red local, abre:

```text
http://192.168.0.123:5173
```

La API debe responder en:

```text
http://192.168.0.123:8000/health
```

Si otro equipo de la misma Wi-Fi no puede entrar, revisa el Firewall de Windows y permite conexiones entrantes a los puertos `5173` y `8000` solo para redes privadas.

La interfaz permite:

- Cargar un expediente PDF.
- Ver bandeja de expedientes.
- Revisar estado de procesamiento.
- Consultar datos extraidos.
- Consultar documentos detectados.
- Ver checklist de validaciones.
- Ver alertas y evidencias.
- Ver veredicto sugerido.
- Reprocesar un expediente despues de corregir OCR/configuracion.
- Exportar un informe JSON desde el navegador.

Mientras un PDF se procesa, el dashboard actualiza estado y detalle en segundo plano sin recargar la vista completa ni perder la seleccion actual.

Nota de seguridad: esta fase no incluye autenticacion ni roles. Usar solo en entorno local o intranet controlada; no exponer el backend ni el dashboard en red publica con expedientes reales.

## Ejecutar con Docker Compose

```bash
docker compose up --build
```

Servicios incluidos en esta fase:

- `backend`: API FastAPI.
- `frontend`: dashboard React/Vite.
- `db`: PostgreSQL.

Para regenerar segmentacion, datos extraidos y validaciones desde el texto OCR ya guardado, sin volver a ejecutar OCR:

```bash
docker compose exec backend python scripts/rebuild_artifacts_from_text.py
```

Este comando es util despues de ajustar patrones de extraccion o reglas de validacion.

Nota: la escritura de metadatos de expedientes se realiza con bloqueo interno y reemplazo atomico del archivo JSON para evitar corrupcion si se suben varios PDFs al mismo tiempo.

El procesamiento OCR se ejecuta con bloqueo interno para evitar inicializaciones paralelas de PaddleOCR. Si se suben varios PDFs escaneados, se encolan dentro del backend y se procesan uno por uno.

## Pruebas

```bash
cd backend
pytest
```

La prueba incluida verifica que `GET /health` responda correctamente.
Tambien hay pruebas para carga de PDF valido y rechazo de archivo invalido.
La Fase 3 agrega pruebas para extraccion de texto digital y PDF sin texto extraible.
La Fase 4 agrega pruebas con mocks para OCR exitoso, OCR sin texto y OCR no disponible.
La Fase 5 agrega pruebas con textos simulados para carta, orden de servicio, recibo por honorarios, factura, informe y anexos.
La Fase 6 agrega pruebas para RUC, orden de servicio, montos, proveedor, concepto y descripcion del servicio.
La Fase 7 agrega pruebas unitarias para presencia de campos principales, coincidencias de O/S y RUC, montos y detalle del servicio.
La Fase 8 agrega una interfaz React para bandeja, detalle, alertas, checklist y exportacion simple.

## Alcance de esta fase

Incluido:

- Backend FastAPI.
- Endpoint `/health`.
- Endpoint `POST /expedientes/upload`.
- Configuracion por variables de entorno.
- `requirements.txt`.
- `.env.example`.
- `docker-compose.yml` con PostgreSQL.
- Guardado local seguro del PDF.
- Registro de nombre, tamano, fecha de carga y estado.
- Modelo base de expediente.
- Extraccion de texto digital por pagina con PyMuPDF.
- OCR local para paginas sin texto digital.
- Marcado de procedencia del texto: `direct_text` u `ocr`.
- Consulta de texto extraido por expediente.
- Segmentacion documental por palabras clave y patrones.
- Consulta de segmentos por expediente.
- Extraccion de datos clave con regex y normalizacion.
- Consulta de datos extraidos por expediente.
- Motor de reglas de validacion.
- Consulta de validaciones y veredicto sugerido por expediente.
- Dashboard administrativo React/Vite.
- Exportacion local de informe JSON desde la interfaz.
- README de ejecucion.
- Prueba basica.

No incluido todavia:

- Autenticacion.
- Reportes PDF/HTML avanzados.
