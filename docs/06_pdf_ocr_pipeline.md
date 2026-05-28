# 06 - Pipeline PDF/OCR

## 1. Objetivo

Procesar expedientes PDF que pueden estar compuestos por páginas escaneadas, documentos con texto, firmas, sellos y páginas en blanco.

## 2. Flujo recomendado

```text
PDF original
  ↓
Validación de archivo
  ↓
Extracción de metadatos
  ↓
Separación por páginas
  ↓
Extracción directa de texto
  ↓
Si hay poco texto: OCR
  ↓
Normalización de texto
  ↓
Clasificación de página
  ↓
Segmentación por documento
  ↓
Extracción de campos
  ↓
Validación
```

## 3. Validación inicial

Revisar:

- Extensión `.pdf`.
- Tamaño máximo.
- Número de páginas.
- Si está protegido con contraseña.
- Si hay páginas rotadas.
- Si existen páginas en blanco.

## 4. Extracción directa

Usar herramientas como:

- PyMuPDF.
- pdfplumber.

Extraer:

- Texto.
- Posición de texto si es posible.
- Tablas.
- Metadatos básicos.

## 5. OCR

Aplicar OCR cuando:

- La página tiene menos de cierto número de caracteres.
- El texto directo es vacío.
- La página parece ser una imagen escaneada.

Motor configurado para SIVECOM:

- PaddleOCR: buena precisión para escaneos y documentos administrativos, con ejecución local.

Opcion alternativa futura:

- EasyOCR: útil para escaneos.

## 6. Preprocesamiento visual

Antes del OCR:

- Corregir rotación.
- Convertir a escala de grises.
- Aumentar contraste.
- Reducir ruido.
- Binarizar si conviene.
- Renderizar a 200-300 DPI.

## 7. Normalización de texto

Aplicar:

- Convertir a minúsculas para búsqueda.
- Mantener versión original para evidencia.
- Eliminar saltos de línea innecesarios.
- Normalizar espacios.
- Corregir errores comunes:
  - `0/S` → `O/S`
  - `O.S.` → `OS`
  - `S/` → `S/.`
  - `lGV` → `IGV`
  - `R.U.C.` → `RUC`

## 8. Salida por página

Cada página debe generar:

```json
{
  "page_number": 1,
  "text": "...",
  "ocr_used": true,
  "ocr_confidence": 82.5,
  "is_blank": false,
  "rotation_detected": 0,
  "image_path": "storage/pages/expediente_001/page_001.png"
}
```

## 9. Reglas de calidad

- No sobrescribir texto original.
- Guardar texto normalizado separado.
- Guardar método usado.
- Registrar errores de OCR.
- Permitir reprocesamiento.
