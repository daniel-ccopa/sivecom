# 04 - Modelo de Base de Datos

## 1. Principios

La base de datos debe permitir trazabilidad completa. Cada dato extraído debe poder relacionarse con su documento, página y evidencia.

## 2. Tablas principales

### users

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  full_name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL,
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMP DEFAULT now()
);
```

### proveedores

```sql
CREATE TABLE proveedores (
  id SERIAL PRIMARY KEY,
  nombre TEXT,
  ruc CHAR(11) UNIQUE,
  direccion TEXT,
  telefono TEXT,
  email TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

### expedientes

```sql
CREATE TABLE expedientes (
  id SERIAL PRIMARY KEY,
  codigo_interno TEXT UNIQUE,
  archivo_original TEXT NOT NULL,
  fecha_carga TIMESTAMP DEFAULT now(),
  usuario_carga_id INT REFERENCES users(id),
  estado TEXT NOT NULL DEFAULT 'pendiente',
  veredicto_sugerido TEXT,
  veredicto_final TEXT,
  observaciones_finales TEXT,
  procesado_en TIMESTAMP,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);
```

### documentos

```sql
CREATE TABLE documentos (
  id SERIAL PRIMARY KEY,
  expediente_id INT REFERENCES expedientes(id),
  tipo TEXT NOT NULL,
  numero_pagina_inicio INT,
  numero_pagina_fin INT,
  texto_extraido TEXT,
  confianza_ocr NUMERIC(5,2),
  ruta_imagen_generada TEXT,
  metadatos JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

### campos_extraidos

```sql
CREATE TABLE campos_extraidos (
  id SERIAL PRIMARY KEY,
  expediente_id INT REFERENCES expedientes(id),
  documento_id INT REFERENCES documentos(id),
  nombre_campo TEXT NOT NULL,
  valor TEXT,
  valor_normalizado TEXT,
  confianza NUMERIC(5,2),
  pagina INT,
  evidencia TEXT,
  metodo TEXT,
  estado TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

### validaciones

```sql
CREATE TABLE validaciones (
  id SERIAL PRIMARY KEY,
  expediente_id INT REFERENCES expedientes(id),
  tipo TEXT NOT NULL,
  nivel TEXT NOT NULL,
  resultado BOOLEAN NOT NULL,
  descripcion TEXT,
  recomendacion TEXT,
  detalles JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

### alertas

```sql
CREATE TABLE alertas (
  id SERIAL PRIMARY KEY,
  expediente_id INT REFERENCES expedientes(id),
  tipo_alerta TEXT NOT NULL,
  severidad TEXT NOT NULL,
  mensaje TEXT NOT NULL,
  evidencia TEXT,
  pagina INT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

### decisiones

```sql
CREATE TABLE decisiones (
  id SERIAL PRIMARY KEY,
  expediente_id INT REFERENCES expedientes(id),
  usuario_id INT REFERENCES users(id),
  decision TEXT NOT NULL,
  observacion TEXT,
  created_at TIMESTAMP DEFAULT now()
);
```

### audit_logs

```sql
CREATE TABLE audit_logs (
  id SERIAL PRIMARY KEY,
  usuario_id INT REFERENCES users(id),
  accion TEXT NOT NULL,
  entidad TEXT,
  entidad_id INT,
  ip TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT now()
);
```

## 3. Estados recomendados

### Estado de expediente

- `pendiente`
- `procesando`
- `procesado`
- `con_alertas`
- `aprobado`
- `rechazado`
- `revision_manual`
- `error_procesamiento`

### Tipo de documento

- `carta_solicitud`
- `orden_servicio`
- `factura`
- `recibo_honorarios`
- `informe_actividades`
- `anexo_fotografico`
- `constancia`
- `desconocido`
- `pagina_blanco`

### Niveles de alerta

- `info`
- `warning`
- `error`
- `critico`
