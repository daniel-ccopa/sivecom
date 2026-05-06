---
name: deployment-local
description: Use this skill when packaging the app for local or intranet deployment with Docker, PostgreSQL, Redis, and Nginx.
---


# Local Deployment Skill

## Purpose

Preparar el sistema para ejecutarse dentro de una municipalidad o red local.

## When to use

Usar cuando se trabaje en:

- Docker Compose.
- Variables de entorno.
- Configuración de servidor.
- Backups.
- Nginx.
- Documentación de instalación.

## Context files

Leer:

- `docs/10_deployment_local.md`
- `docs/08_security_privacy.md`

## Required behavior

- Crear configuración reproducible.
- Separar desarrollo y producción.
- Definir `.env.example`.
- Configurar volúmenes.
- Configurar backups.
- Documentar pasos de instalación.

## Services

- backend
- frontend
- worker
- db
- redis
- nginx opcional

## Do

- Usar Docker Compose.
- Montar storage persistente.
- Crear healthchecks.
- Preparar backup script.
- Documentar restauración.

## Do not

- No dejar credenciales por defecto en producción.
- No guardar archivos en contenedor sin volumen.
- No exponer base de datos fuera de la red si no es necesario.
- No usar modo debug en producción.

## Acceptance checklist

- [ ] docker compose funciona.
- [ ] variables de entorno documentadas.
- [ ] storage persistente.
- [ ] backup definido.
- [ ] guía de instalación creada.
