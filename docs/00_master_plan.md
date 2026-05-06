# 00 - Master Plan del Proyecto

## 1. Nombre del proyecto

**SIVECOM - Sistema Inteligente de Verificación de Expedientes de Conformidad Municipal**

## 2. Descripción general

SIVECOM será una plataforma web para apoyar la revisión administrativa de expedientes PDF presentados por proveedores o áreas técnicas de una municipalidad. El usuario cargará un único PDF que puede contener carta, orden de servicio, comprobante de pago, informe de actividades, anexos, fotos, firmas y sellos. El sistema extraerá los datos principales, verificará requisitos, marcará alertas y generará un informe de apoyo para la conformidad.

## 3. Problema identificado

La revisión manual de expedientes demanda tiempo, es repetitiva y puede generar errores por cansancio, omisión o dificultad para comparar datos entre varias páginas. Un expediente puede contener documentos escaneados, páginas en blanco, firmas, montos, fechas y referencias que deben coincidir.

## 4. Solución propuesta

Crear un sistema que automatice la lectura inicial del expediente y aplique reglas de validación. El sistema no reemplaza al funcionario, pero reduce el tiempo de revisión y aumenta la trazabilidad.

## 5. Objetivo general

Diseñar e implementar un sistema web para la extracción, validación y revisión asistida de expedientes PDF de conformidad de servicios municipales.

## 6. Objetivos específicos

1. Implementar un módulo de carga y procesamiento de PDFs.
2. Extraer texto de documentos digitales y escaneados mediante OCR.
3. Clasificar páginas por tipo de documento.
4. Extraer datos clave como proveedor, RUC, orden de servicio, fechas y montos.
5. Aplicar reglas de validación documental, financiera y temporal.
6. Presentar alertas y veredicto en un dashboard.
7. Permitir revisión humana y exportación de informe.
8. Mantener historial, auditoría y trazabilidad.

## 7. Usuarios objetivo

- Personal administrativo.
- Área de logística.
- Área usuaria o área técnica.
- Jefes de unidad.
- Auditoría o control interno.
- Administrador del sistema.

## 8. Alcance del MVP

Incluye:

- Carga de PDF único.
- Extracción de texto.
- OCR para documentos escaneados.
- Segmentación por tipo de documento.
- Extracción de datos principales.
- Validación de checklist.
- Validación de montos, fechas y coincidencias.
- Dashboard de resultados.
- Exportación de informe.
- Registro de auditoría.

## 9. Fuera de alcance inicial

No incluye en el MVP:

- Integración real con SIAF.
- Firma digital avanzada.
- Pago automático.
- Validación legal definitiva.
- Reconocimiento perfecto de firmas manuscritas.
- Envío automático de documentos a entidades externas.
- Entrenamiento de IA profunda con documentos sensibles sin anonimización.

## 10. Tecnologías

- Backend: FastAPI.
- Procesamiento de PDF: PyMuPDF, pdfplumber, pdf2image.
- OCR: Tesseract, EasyOCR o PaddleOCR.
- Validación: motor de reglas propio.
- Base de datos: PostgreSQL.
- Cola de tareas: Celery/RQ + Redis.
- Frontend: React + TypeScript.
- Estilos: Tailwind CSS.
- Exportación: HTML/PDF.
- Despliegue: Docker Compose.

## 11. Módulos del sistema

1. Módulo de autenticación y roles.
2. Módulo de carga de expedientes.
3. Módulo de procesamiento PDF/OCR.
4. Módulo de clasificación documental.
5. Módulo de extracción de datos.
6. Módulo de validación.
7. Módulo de alertas.
8. Módulo de dashboard.
9. Módulo de revisión humana.
10. Módulo de reportes.
11. Módulo de auditoría.

## 12. Criterios de éxito

El proyecto será exitoso si:

- Procesa expedientes en PDF sin que el usuario los separe manualmente.
- Extrae datos clave con evidencia por página.
- Detecta documentos faltantes.
- Detecta montos y fechas inconsistentes.
- Genera un veredicto claro.
- Permite revisión humana final.
- Guarda historial auditable.
- Reduce el tiempo de revisión administrativa.

## 13. Estrategia de desarrollo

1. Primero desarrollar un prototipo con 5 a 10 expedientes reales anonimizados.
2. Crear reglas simples y verificables.
3. Medir errores frecuentes de OCR.
4. Mejorar reglas con fuzzy matching.
5. Crear dashboard funcional.
6. Agregar auditoría y exportación.
7. Preparar despliegue local.
