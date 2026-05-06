# 08 - Seguridad, privacidad y cumplimiento

## 1. Principio central

Los expedientes pueden contener datos sensibles, firmas, RUC, DNI, domicilios y documentos administrativos. El sistema debe proteger esa información.

## 2. Reglas de seguridad

- Autenticación obligatoria.
- Roles y permisos.
- Contraseñas hasheadas.
- HTTPS si se despliega en red.
- Logs sin datos sensibles completos.
- Control de acceso por rol.
- Copias de seguridad.
- Auditoría de acciones.

## 3. Manejo de archivos

- Guardar PDFs en carpeta segura.
- No exponer rutas internas.
- Generar nombres de archivo no predecibles.
- Validar tipo MIME.
- Limitar tamaño máximo.
- Evitar ejecución de archivos subidos.

## 4. Protección de datos personales

- Enmascarar RUC/DNI en vistas no autorizadas.
- No mostrar firmas en reportes públicos.
- No usar documentos reales para pruebas sin anonimizar.
- No enviar PDFs a APIs externas salvo autorización expresa.

## 5. Auditoría

Registrar:

- Usuario que subió expediente.
- Fecha y hora.
- IP.
- Acción realizada.
- Cambios de estado.
- Decisión final.
- Exportación de reportes.

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| OCR interpreta mal un monto | Mostrar evidencia y requerir revisión manual |
| Documento sensible expuesto | Roles, enmascaramiento y logs seguros |
| Expediente duplicado | Hash de archivo y número de O/S |
| Decisión automática errónea | Revisión humana obligatoria |
| Pérdida de archivos | Backups programados |
