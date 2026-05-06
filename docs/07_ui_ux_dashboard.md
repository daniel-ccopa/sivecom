# 07 - UI/UX Dashboard

## 1. Objetivo de la interfaz

La interfaz debe permitir que un administrativo entienda rápidamente si un expediente procede, debe revisarse o debe rechazarse.

## 2. Principios de diseño

- Simple.
- Claro.
- Auditable.
- Sin exceso de texto técnico.
- Con evidencia visible.
- Con colores para severidad.
- Con opción de ver detalles.

## 3. Pantallas principales

### Login

- Correo.
- Contraseña.
- Recuperación de acceso, opcional.

### Bandeja de expedientes

Columnas:

- Código.
- Fecha de carga.
- Proveedor.
- Orden de servicio.
- Monto.
- Estado.
- Veredicto.
- Alertas.
- Responsable.
- Acciones.

Filtros:

- Estado.
- Fecha.
- Proveedor.
- Severidad.
- Número de O/S.

### Carga de expediente

- Arrastrar PDF.
- Botón subir.
- Validación de tamaño.
- Mensaje de privacidad.
- Progreso del procesamiento.

### Dashboard del expediente

Secciones:

1. Resumen general.
2. Veredicto sugerido.
3. Checklist documental.
4. Datos extraídos.
5. Alertas.
6. Vista de páginas.
7. Evidencia.
8. Decisión final.

### Vista de comparación

Mostrar datos por documento:

| Campo | Carta | O/S | Comprobante | Informe | Estado |
|---|---|---|---|---|---|
| Número O/S | 000000 | 000000 | - | 000000 | OK |
| Monto | - | S/ 1500 | S/ 1500 | - | OK |
| RUC | - | 20... | 20... | - | OK |

### Decisión final

Opciones:

- Procede conformidad.
- Rechazar.
- Revisión manual.
- Solicitar subsanación.

Debe pedir observación si:

- Se aprueba con advertencias.
- Se rechaza.
- Se cambia el veredicto sugerido.

## 4. Componentes visuales

- Card de resumen.
- Badge de estado.
- Tabla de alertas.
- Viewer de PDF o imagen por página.
- Panel lateral de evidencia.
- Botón exportar.

## 5. Mensajes recomendados

- "El expediente fue procesado correctamente."
- "Se encontraron alertas que requieren revisión manual."
- "No se pudo extraer el RUC con suficiente confianza."
- "El monto del comprobante supera el monto de la orden de servicio."
- "La decisión final fue registrada correctamente."
