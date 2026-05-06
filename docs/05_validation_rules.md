# 05 - Reglas de Validación

## 1. Principio general

Cada regla debe ser explicable. El sistema debe mostrar qué dato revisó, dónde lo encontró y por qué generó una alerta.

## 2. Checklist documental

### Documentos obligatorios

- Carta de solicitud de conformidad.
- Orden de servicio.
- Comprobante de pago: factura o recibo por honorarios.
- Informe de actividades o informe técnico.
- Evidencia de prestación del servicio, si corresponde.
- Firma o sello visible/probable.

### Resultado

- Si falta documento obligatorio: `ERROR`.
- Si existe documento pero tiene baja confianza: `WARNING`.
- Si todos están presentes: `OK`.

## 3. Validación de orden de servicio

Campos a comparar:

- Número de orden de servicio.
- Proveedor.
- RUC.
- Monto total.
- Concepto.
- Fecha de emisión.

Reglas:

- La orden de servicio debe aparecer al menos una vez.
- El número de O/S debe coincidir entre carta, informe y comprobante.
- Si hay dos números diferentes de O/S, marcar `ERROR`.
- Si solo se detecta en un documento, marcar `WARNING`.

## 4. Validación de proveedor y RUC

Reglas:

- El RUC debe tener 11 dígitos.
- El RUC en comprobante debe coincidir con el RUC de la orden de servicio.
- El nombre del proveedor debe tener coincidencia aproximada con fuzzy matching.
- Si el RUC no coincide: `ERROR`.
- Si el nombre varía ligeramente pero el RUC coincide: `WARNING` o `OK` según confianza.

## 5. Validación de montos

Reglas:

- Monto total del comprobante debe ser menor o igual al monto total de la O/S.
- Si la O/S tiene subtotal, IGV y total, verificar:
  - subtotal + IGV = total.
  - IGV aproximado = subtotal * 0.18.
- Permitir tolerancia de redondeo: S/ 0.05.
- Si comprobante excede O/S: `ERROR`.
- Si hay diferencia menor por redondeo: `WARNING`.
- Si todo coincide: `OK`.

## 6. Validación de fechas

Reglas:

- Fecha de comprobante no debe ser muy anterior a la fecha de emisión de O/S.
- Fecha de informe debe estar después o cerca del periodo de ejecución.
- Fecha de carta debe ser posterior a la culminación del servicio.
- Si una fecha aparece en formato ambiguo, marcar baja confianza.
- Si fecha final es anterior a fecha inicial: `ERROR`.

## 7. Coherencia del informe de actividades

Reglas:

- El informe debe mencionar el servicio contratado o términos relacionados.
- Debe contener actividades realizadas.
- Debe contener conclusiones o recomendaciones.
- Si el servicio es mantenimiento, buscar palabras como:
  - mantenimiento
  - revisión
  - soporte
  - configuración
  - equipos
  - cámaras
  - informe
- Si el informe no guarda relación semántica mínima con el concepto: `WARNING` o `ERROR`.

## 8. Firmas y sellos

Reglas de baja complejidad:

- Buscar zonas con trazos/firmas mediante análisis visual simple.
- Buscar texto cercano como:
  - Atentamente
  - Firma
  - V°B°
  - Sello
  - Responsable
- Si el documento requiere firma y no se detecta ninguna pista: `WARNING`.

## 9. Duplicados

Reglas:

- Si el número de O/S ya fue procesado con el mismo comprobante, marcar `ERROR`.
- Si el proveedor presenta expedientes muy similares en periodo corto, marcar `WARNING`.
- Si el archivo PDF tiene hash igual a uno anterior, marcar `ERROR`.

## 10. Veredicto sugerido

- Si existe al menos un error crítico: `rechazar`.
- Si existen errores no críticos o datos dudosos: `revision_manual`.
- Si solo existen advertencias leves: `revision_manual` o `procede_conformidad_condicionada`.
- Si todo está correcto: `procede_conformidad`.
