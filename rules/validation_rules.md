# Reglas iniciales de validación

## R001 - Documentos obligatorios

Debe existir al menos:

- carta_solicitud
- orden_servicio
- comprobante: factura o recibo_honorarios
- informe_actividades

Resultado:
- Falta uno: ERROR.
- Baja confianza: WARNING.
- Todos presentes: OK.

## R002 - Número de orden de servicio

El número de O/S debe coincidir entre documentos.

Resultado:
- Coincide: OK.
- Falta en algún documento no crítico: WARNING.
- Aparece diferente: ERROR.

## R003 - RUC del proveedor

El RUC debe tener 11 dígitos y coincidir entre O/S y comprobante.

Resultado:
- Coincide: OK.
- No encontrado: WARNING.
- Diferente: ERROR.

## R004 - Monto total

El monto total del comprobante no debe superar el monto total de la O/S.

Resultado:
- Menor o igual: OK.
- Mayor: ERROR.
- No se pudo extraer: WARNING.

## R005 - IGV

Si se detectan subtotal, IGV y total, verificar que subtotal + IGV = total.

Tolerancia: S/ 0.05.

Resultado:
- Correcto: OK.
- Diferencia leve: WARNING.
- Diferencia importante: ERROR.

## R006 - Fechas

Validar coherencia temporal.

Resultado:
- Fechas coherentes: OK.
- Fecha dudosa: WARNING.
- Fecha final antes de inicial: ERROR.

## R007 - Informe coherente

El informe debe contener términos relacionados con el servicio contratado.

Resultado:
- Coherente: OK.
- Poco claro: WARNING.
- No relacionado: ERROR.

## R008 - Firma o sello probable

Detectar firma/sello por texto y análisis visual simple.

Resultado:
- Evidencia probable: OK.
- No encontrado: WARNING.

## R009 - Expediente duplicado

Comparar hash del PDF y número de O/S + comprobante.

Resultado:
- No duplicado: OK.
- Posible duplicado: WARNING.
- Duplicado exacto: ERROR.

## R010 - Páginas en blanco

Detectar páginas en blanco.

Resultado:
- No afecta: INFO.
- Página en blanco dentro de documento importante: WARNING.
