# 10 - Despliegue Local/Intranet

## 1. Objetivo

Permitir que el sistema funcione dentro de la municipalidad sin depender de internet.

## 2. Opción recomendada

Usar Docker Compose con:

- Backend FastAPI.
- Frontend React.
- PostgreSQL.
- Redis.
- Worker Celery/RQ.
- Nginx, opcional.

## 3. Variables de entorno

Crear archivo `.env`:

```env
APP_ENV=local
DATABASE_URL=postgresql://sivecom:sivecom@db:5432/sivecom
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change_me
UPLOAD_DIR=/app/storage/uploads
MAX_UPLOAD_MB=50
OCR_LANGUAGE=es
PADDLE_OCR_BASE_DIR=/app/storage/paddleocr_models
PADDLE_USE_GPU=false
```

## 4. Servicios mínimos

```yaml
services:
  backend:
    build: ./backend
    env_file: .env
    depends_on:
      - db
      - redis

  worker:
    build: ./backend
    command: celery -A app.workers.celery_app worker --loglevel=info
    env_file: .env
    depends_on:
      - backend
      - redis

  frontend:
    build: ./frontend
    depends_on:
      - backend

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: sivecom
      POSTGRES_USER: sivecom
      POSTGRES_PASSWORD: sivecom

  redis:
    image: redis:7
```

## 5. Backups

Respaldar:

- Base de datos.
- PDFs originales.
- Reportes generados.
- Logs de auditoría.

## 6. Recomendaciones

- Usar disco dedicado para almacenamiento.
- Programar backups diarios.
- Limitar acceso por red local.
- Usar HTTPS con certificado interno si es posible.
- Crear usuario administrador inicial.
