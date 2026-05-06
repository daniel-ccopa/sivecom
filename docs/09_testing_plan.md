# 09 - Plan de Pruebas

## 1. Objetivo

Asegurar que SIVECOM procese expedientes de forma confiable, auditable y útil para el usuario administrativo.

## 2. Tipos de pruebas

### Pruebas unitarias

- Extracción de RUC.
- Extracción de montos.
- Extracción de fechas.
- Cálculo de IGV.
- Clasificación por palabras clave.
- Reglas de validación.

### Pruebas de integración

- Subida de PDF.
- Procesamiento en worker.
- Guardado en base de datos.
- Consulta de resultados.
- Generación de informe.

### Pruebas de UI

- Carga de expediente.
- Visualización de alertas.
- Decisión final.
- Filtros de bandeja.
- Exportación.

### Pruebas de seguridad

- Acceso sin login.
- Permisos por rol.
- Archivos inválidos.
- PDFs muy grandes.
- Intento de subir archivo no PDF.

## 3. Casos de prueba esenciales

1. PDF correcto con todos los documentos.
2. PDF sin comprobante.
3. PDF sin orden de servicio.
4. PDF con monto diferente.
5. PDF con RUC diferente.
6. PDF con fechas incoherentes.
7. PDF escaneado con OCR.
8. PDF con páginas en blanco.
9. PDF duplicado.
10. PDF con texto de baja calidad.

## 4. Métricas de calidad

- Porcentaje de documentos clasificados correctamente.
- Porcentaje de campos extraídos correctamente.
- Tiempo promedio por expediente.
- Número de alertas falsas.
- Número de errores no detectados.
- Satisfacción del usuario administrativo.

## 5. Regla de aprobación

Antes de considerar listo el MVP:

- 90% de documentos principales deben ser clasificados correctamente en pruebas internas.
- Montos y RUC deben tener validación conservadora.
- Toda alerta crítica debe generar revisión manual o rechazo.
- Ninguna decisión final debe aplicarse sin intervención humana.
