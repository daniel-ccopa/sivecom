# Patrones iniciales de extracción

> Estos patrones deben implementarse y probarse. Ajustarlos con expedientes reales anonimizados.

## RUC

```regex
(?:R\.?U\.?C\.?|RUC)\s*[:N°º-]*\s*(\d{11})
```

## Orden de servicio

```regex
(?:ORDEN\s+DE\s+SERVICIO|O\/S|OS|O\.S\.)\s*(?:N[°º]|No\.?|Nro\.?)?\s*[:\-]?\s*([0-9]{4,10})
```

## Fecha textual

```regex
(\d{1,2})\s+de\s+([A-Za-zÁÉÍÓÚáéíóú]+)\s+(?:de|del)\s+(\d{4})
```

## Fecha numérica

```regex
(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})
```

## Monto soles

```regex
(?:S\/\.?|Soles?)\s*([0-9]{1,3}(?:[,\.][0-9]{3})*(?:[,\.][0-9]{2})?)
```

## Total

```regex
(?:TOTAL|MONTO\s+TOTAL|IMPORTE\s+TOTAL|TOTAL\s+NETO\s+RECIBIDO)\s*[:\-]?\s*(?:S\/\.?)?\s*([0-9.,]+)
```

## IGV

```regex
(?:IGV|I\.G\.V\.)\s*(?:\(?18\s*%\)?)?\s*[:\-]?\s*(?:S\/\.?)?\s*([0-9.,]+)
```
