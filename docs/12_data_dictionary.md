# 12 - Diccionario de Datos

## Expediente

| Campo | Descripción |
|---|---|
| codigo_interno | Código único generado por el sistema |
| archivo_original | Ruta del PDF subido |
| estado | Estado del procesamiento |
| veredicto_sugerido | Resultado automático |
| veredicto_final | Decisión humana |
| observaciones_finales | Comentario del usuario |

## Documento

| Campo | Descripción |
|---|---|
| tipo | Tipo de documento detectado |
| numero_pagina_inicio | Página inicial |
| numero_pagina_fin | Página final |
| texto_extraido | Texto detectado |
| confianza_ocr | Confianza promedio del OCR |
| metadatos | Datos específicos del documento |

## Campo extraído

| Campo | Descripción |
|---|---|
| nombre_campo | Ejemplo: ruc, monto_total, numero_os |
| valor | Valor tal como apareció |
| valor_normalizado | Valor limpio para comparación |
| confianza | Nivel de confianza |
| pagina | Página de evidencia |
| evidencia | Fragmento de texto |
| metodo | regex, ocr, tabla, fuzzy |
| estado | encontrado, no_encontrado, baja_confianza |

## Validación

| Campo | Descripción |
|---|---|
| tipo | Nombre de la regla |
| nivel | info, warning, error, critico |
| resultado | true/false |
| descripcion | Explicación |
| recomendacion | Qué debe hacer el usuario |
| detalles | JSON con evidencia adicional |
