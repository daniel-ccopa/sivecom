# Patrones actuales de extraccion

El alcance actual solo extrae los campos principales necesarios para una revision menos exigente.

## RUC

```regex
(?:R\.?U\.?C\.?|RUC)\s*[:N-]*\s*(\d{11})
```

## Orden de servicio

```regex
(?:ORDEN\s+DE\s+SERVICIO|O/S|OS|O\.S\.)\s*(?:N|No\.?|Nro\.?)?\s*[:\-]?\s*([0-9]{4,10})
```

Tambien se contemplan variantes OCR frecuentes de PaddleOCR:

- `SERVlClO` en lugar de `SERVICIO`.
- `NRO.00cO452` y `00015 82`, normalizando `O/o/C/c` como cero cuando aparecen dentro del numero y descartando separadores.
- `OOO1S42`, normalizando `S/s` como cinco cuando aparece dentro del numero de orden.
- `00001378 2025-00018035`, cortando el anio o codigo de tramite pegado al numero de O/S y conservando el formato visible principal, por ejemplo `0001378`.
- Sufijos OCR o de pagina como `0001582 2` o `00cO452 CO`, descartando tokens cortos anexados despues de un numero de O/S ya completo.
- Candidatos aislados de O/S dentro de una pagina de orden se descartan cuando otra O/S aparece repetida en varios tipos de documento, para evitar que anexos o copias de otras entidades contaminen el expediente principal.
- Para resolver conflictos, la comparacion ignora ceros iniciales de relleno: `001089` y `0001089` se consideran el mismo numero, aunque se conserva el valor visible extraido como evidencia.

## Monto total / entregable

```regex
(?:TOTAL|MONTO\s+TOTAL|IMPORTE\s+TOTAL|TOTAL\s+NETO\s+RECIBIDO)\s*[:\-]?\s*(?:S/\.?)?\s*([0-9.,]+)
```

Para paginas de orden de servicio con OCR ruidoso, si el texto contiene senales como `unidad ejecutora`, `nro identificacion`, `afectacion presupuestal` u `orden de servicio`, se toma como respaldo el mayor monto decimal visible mayor o igual a 100.

En facturas, cuando `Importe Total` aparece como bloque con varios importes, se toma el ultimo monto antes de `Informacion de la detraccion`, `Leyenda` o el cierre del comprobante. Esto evita confundir `Valor Venta` con el total de factura.

En ordenes de servicio con formato tabular de PaddleOCR se prioriza el monto que aparece despues de `SERVICIO SERVICIOS DIVERSOS` o `Vienen/Van`. Esto evita tomar valores de afectacion presupuestal o referencias como si fueran el monto total de la orden.

En recibos por honorarios, el monto siempre se guarda como `monto_entregable`, aunque el texto mencione la orden de servicio. Se contemplan variantes OCR como `Total pot honoraries`.

## Cronograma de entregables

Se extraen datos de forma de pago cuando aparecen en la orden de servicio o comprobante:

- `numero_entregables`: detecta frases como `EN 02 ENTREGABLES` o `UNICO ENTREGABLE`.
- `porcentaje_entregable`: detecta porcentajes por entregable, por ejemplo `PRIMER ENTREGABLE: (50% DEL TOTAL)`.

Se contemplan variantes OCR frecuentes:

- `o2 ENTREGABLEs` se normaliza como `2`.
- `5Os DEL TOTAL` y `SOS DEL TOTAL` se interpretan como `50%` cuando aparecen junto a `ENTREGABLE`.
- `SEGUND0 ENTREGABLE` se interpreta como segundo entregable.

## Concepto / descripcion

```regex
(?:Concepto|Descripcion|Detalle)\s*(?:del servicio)?\s*[:\-]\s*(.+)
```

Patrones adicionales:

- `ASUNTO: ...` hasta `REF`, `REFERENCIA`, `FECHA` o el inicio del cuerpo.
- `Por concepto de ...` y variantes OCR como `Por concopto de ...` hasta `Observacion`, `Fecha` o `Total`.
- `Descripcion ...` sin dos puntos en ordenes de servicio, deteniendose antes de `ORDEN QUE SE`, `AFECTACION`, `Meta`, `Van` o `Total`.
- `ORDEN QUE SE EMITE PARA LA CONTRATACION DE ...` para ordenes de servicio donde el concepto esta dentro del texto largo.
- `QUE SE EMITE PARA LA CONTRATACION DE ...` cuando OCR deforma `ORDEN` como `ORI>EN`.
- `Par concepto de ...` ademas de `Por concepto de ...` para variantes OCR.
- Se descartan valores que empiezan con `Total S/`, `Referencia`, `Afectacion presupuestal`, `Codigo`, `Unid. Med.`, `Lugar y plazo` o `Forma de pago`.

## Proveedor

Ademas de etiquetas como `Proveedor`, `Razon Social` o `Senor(es)`, se toma la primera linea probable de cabecera en recibos/facturas cuando aparece antes de `Recibo de`, `Recibo por honorarios`, `Factura electronica` o `RUC`. Se descartan lineas de direccion, telefono, municipio y otros encabezados administrativos.

La limpieza de proveedor descarta prefijos OCR de pagina como `02 - 01`, simbolos iniciales, profesiones/direcciones y metadatos administrativos que aparezcan en la misma linea.

Tambien se descartan direcciones detectadas falsamente como proveedor y se usa `DE: ... PROVEEDOR` cuando aparece en cartas.

En facturas se ignora el RUC del receptor/cliente municipal cuando aparece despues de `Senor(es)`, `Direccion del Receptor` o `Direccion del Cliente`, conservando el RUC del emisor/proveedor.

Tambien se contempla:

- `: RAZON SOCIAL. Proveedor de servicios` en cartas.
- `proveedor la empresa RAZON SOCIAL - con RUC` en actas o documentos de internamiento.
- `DE: ING. NOMBRE APELLIDOS RESPONSABLE ...` en cartas e informes, para casos donde el mismo proveedor/responsable aparece con orden de nombres diferente al recibo.
- `Sefior(es): APELLIDOS NOMBRES Tipo de Proceso ...`, cortando antes de `Tipo de Proceso`, `CCI` o `Contrato`.
- Se bloquean listas de anexos como `Segundo. - Anexo... COPIA DE DNI ORDEN DE SERVICIO...` para que no se registren como proveedor aunque la pagina mencione recibos u ordenes.

## Correccion de outliers OCR

Cuando un RUC aparece repetido en varios documentos y existe un unico candidato con un solo digito distinto, se descarta ese candidato como probable ruido OCR. La regla solo aplica si hay soporte repetido para el RUC dominante; no inventa ni reemplaza datos no encontrados.

## Campos descartados

No se extraen en el alcance actual:

- Fechas.
- IGV.
- Valor venta.
- Adjuntos mencionados.
- Firmantes o cargos.
- Numero de carta o informe.
- Actividades o dias trabajados.
