# 02 - PRD: Product Requirements Document

## 1. Producto

Sistema web para validación asistida de expedientes PDF de conformidad de servicios.

## 2. Problema de usuario

El personal administrativo necesita revisar expedientes extensos y comparar datos repetidos entre carta, orden de servicio, comprobante e informe. Esta revisión manual consume tiempo y puede generar errores.

## 3. Usuarios y roles

### Administrador del sistema
- Gestiona usuarios.
- Configura reglas.
- Visualiza logs.

### Administrativo
- Carga expedientes.
- Revisa resultados.
- Aprueba, rechaza o envía a revisión.

### Jefe de área
- Valida decisiones.
- Revisa alertas importantes.

### Auditor
- Consulta historial.
- Exporta reportes.

## 4. Funcionalidades obligatorias del MVP

### Carga de expediente
- Subir PDF único.
- Validar tamaño máximo.
- Validar tipo de archivo.
- Mostrar progreso de procesamiento.

### Procesamiento
- Detectar páginas en blanco.
- Extraer texto directo.
- Aplicar OCR si no hay texto suficiente.
- Guardar imagen renderizada de cada página.

### Clasificación documental
- Identificar carta.
- Identificar orden de servicio.
- Identificar comprobante.
- Identificar informe de actividades.
- Identificar anexos/fotos.
- Marcar páginas desconocidas.

### Extracción de datos
- Número de orden de servicio.
- Fecha de emisión.
- Proveedor.
- RUC.
- Monto subtotal.
- IGV.
- Monto total.
- Concepto del servicio.
- Área solicitante.
- Fechas de informe.
- Número de comprobante.
- Lista de documentos adjuntos.

### Validación
- Checklist de documentos obligatorios.
- Coincidencia de número de orden de servicio.
- Coincidencia de proveedor/RUC.
- Coincidencia de montos.
- Cálculo de IGV.
- Coherencia de fechas.
- Coherencia entre servicio contratado e informe.
- Posible duplicidad de expediente.
- Detección de páginas en blanco relevantes.
- Verificación de presencia probable de firmas/sellos.

### Dashboard
- Resumen del expediente.
- Veredicto sugerido.
- Lista de alertas.
- Checklist.
- Vista de documentos detectados.
- Vista de evidencia por página.
- Botón para decisión final.

### Exportación
- Exportar informe en PDF o HTML.
- Incluir validaciones, evidencias y decisión final.

## 5. Veredictos posibles

- `procede_conformidad`: no hay errores críticos.
- `rechazar`: existe error crítico.
- `revision_manual`: existen alertas o datos con baja confianza.
- `pendiente`: procesamiento incompleto.

## 6. Criterios de aceptación

- El sistema debe procesar un PDF escaneado.
- El sistema debe diferenciar texto encontrado por OCR y texto extraído directamente.
- Toda alerta debe tener evidencia.
- El usuario debe poder ver en qué página aparece el dato.
- La decisión final debe quedar registrada con usuario, fecha y observación.
- El sistema no debe enviar documentos a internet sin autorización.
