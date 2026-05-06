# 15 - Notas de origen y adaptación

Este paquete fue diseñado a partir de la idea de desarrollar un sistema web para validar expedientes PDF municipales de conformidad de servicios.

## Elementos observados en el expediente de ejemplo

El expediente usado como referencia contiene documentos similares a:

- Carta de solicitud de conformidad.
- Informe técnico o informe de actividades.
- Recibo por honorarios electrónico.
- Orden de servicio.
- Páginas en blanco o separadoras.
- Firmas y sellos.

## Decisión de diseño

Por la naturaleza de estos documentos, el sistema debe:

- Procesar un PDF completo sin exigir separación manual.
- Usar OCR porque muchos documentos son escaneados.
- Clasificar páginas por palabras clave.
- Extraer datos con reglas y evidencia.
- Mantener revisión humana obligatoria.
- Guardar trazabilidad completa.

## Nota de privacidad

Los expedientes reales deben anonimizarse antes de usarse como datos de prueba o de entrenamiento.
