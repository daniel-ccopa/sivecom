# Reglas actuales de validacion

El motor de validacion queda enfocado en los datos principales del expediente. La finalidad es apoyar la revision administrativa sin exigir documentos o datos secundarios que pueden faltar por OCR o por formato del expediente.

## Campos principales

El sistema intenta extraer:

- Numero de orden de servicio.
- RUC del proveedor.
- Nombre o razon social del proveedor.
- Monto total de la O/S.
- Monto del entregable o comprobante.
- Concepto.
- Descripcion del servicio.

## R001 - Campos principales detectados

Verifica presencia de los campos principales.

Resultado:

- Todos presentes: OK.
- Faltan datos principales: ADVERTENCIA.

No genera rechazo automatico por ausencia de carta, fechas, adjuntos, firmantes o sellos.

## R000 - Documentos obligatorios

Verifica que el expediente tenga los 4 documentos obligatorios para conformidad:

- Carta.
- Orden de servicio.
- Informe de actividades o acta de entrega equivalente.
- Comprobante de pago: recibo por honorarios o factura.

Resultado:

- Todos presentes: OK.
- Alguno presente con baja confianza: ADVERTENCIA.
- Falta uno o mas documentos obligatorios: ERROR.

El mensaje debe indicar exactamente que documento falta y que documentos si fueron detectados, con paginas y evidencia.

## R002 - Numero de orden de servicio

Revisa que los numeros de O/S extraidos no entren en conflicto.

Resultado:

- Unico valor detectado: OK.
- No encontrado o valores diferentes: ADVERTENCIA.

La comparacion ignora ceros iniciales de relleno para no marcar conflicto entre variantes como `001089` y `0001089`, conservando siempre la evidencia original.

## R003 - RUC del proveedor

Revisa formato de 11 digitos y consistencia de RUC.

Resultado:

- RUC valido y unico: OK.
- No encontrado, formato invalido o valores diferentes: ADVERTENCIA.

## R004 - Revision de montos

Compara monto total de la O/S contra monto del entregable/comprobante cuando ambos existan.

Resultado:

- Entregable menor o igual a la O/S: OK.
- Faltan montos suficientes para comparar: ADVERTENCIA.
- Monto del entregable supera la O/S: ERROR.

## R008 - Cronograma de entregables

Valida la forma de pago indicada en la O/S cuando se detectan entregables y porcentajes.

Resultado:

- Si no se detecta cronograma, no genera alerta adicional y se mantiene R004.
- Si la O/S indica porcentajes por entregable, los porcentajes deben sumar 100%.
- El monto del comprobante debe coincidir con alguno de los montos programados por entregable.
- Si hay un unico entregable, el comprobante debe coincidir con el monto total de la O/S.
- Si faltan montos o el OCR no permite comparar, genera ADVERTENCIA con evidencia.

## R005 - Concepto y descripcion

Verifica que se haya extraido concepto y descripcion del servicio.

Resultado:

- Los dos datos fueron detectados: OK.
- Falta alguno: ADVERTENCIA.

## R006 - Coincidencia de proveedor

Compara los nombres o razones sociales del proveedor detectados en los documentos.
La comparacion usa tokens normalizados, por lo que acepta el mismo nombre en distinto orden, por ejemplo `nombre apellidos` frente a `apellidos nombre`, siempre que los componentes principales coincidan.

Resultado:

- Unico proveedor o nombres compatibles: OK.
- No se encontro proveedor o hay baja coincidencia entre nombres: ADVERTENCIA.

## R007 - Coherencia del servicio

Compara el concepto o descripcion del servicio entre los documentos donde se pudo extraer.

No usa como base textos administrativos de carta como `solicito conformidad de pago` o `primer entregable` cuando no describen el servicio contratado.

Resultado:

- Coincidencia textual suficiente entre documentos: OK.
- Si el concepto solo aparece en la orden de servicio, pero los 4 documentos obligatorios fueron detectados y no hay texto contradictorio: OK.
- Solo se encontro en un documento sin soporte documental suficiente o no hay coincidencia clara: ADVERTENCIA.

## Reglas descartadas en esta etapa

Para reducir exigencia y evitar rechazos por datos secundarios, el motor actual no valida automaticamente:

- Fechas de emision.
- Periodo del servicio.
- Lista de documentos adjuntos.
- Numero de carta o informe.
- Nombres y cargos de firmantes.
- Valor venta e IGV.
- Actividades o dias trabajados.
- Posibles duplicados.
- Firmas o sellos.
