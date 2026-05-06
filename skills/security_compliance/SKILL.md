---
name: security-compliance
description: Use this skill when implementing authentication, authorization, privacy protections, secure file handling, and data governance.
---


# Security and Compliance Skill

## Purpose

Proteger documentos administrativos y datos sensibles.

## When to use

Usar cuando se trabaje en:

- Login.
- Roles.
- Permisos.
- Manejo de archivos.
- Logs.
- Privacidad.
- Backups.

## Context files

Leer:

- `docs/08_security_privacy.md`
- `AGENTS.md`

## Roles

- admin
- administrativo
- jefe_area
- auditor
- solo_lectura

## Required behavior

- Autenticación obligatoria.
- Autorización por rol.
- Password hashing.
- JWT o sesiones seguras.
- Expiración de sesión.
- Validación de archivos.
- Enmascaramiento de datos.
- Logs seguros.

## File security

- Validar tipo MIME.
- Limitar tamaño.
- Guardar en ruta no pública.
- Generar nombre interno único.
- Escanear estructura básica.
- No ejecutar contenido.

## Do

- Usar variables de entorno.
- Crear política de permisos.
- Registrar auditoría.
- Separar datos públicos y privados.
- Preparar backups.

## Do not

- No subir documentos a servicios externos sin permiso.
- No imprimir RUC/DNI completos en logs.
- No exponer rutas internas.
- No permitir acceso anónimo.

## Acceptance checklist

- [ ] Login protegido.
- [ ] Roles funcionando.
- [ ] Upload seguro.
- [ ] Logs sin datos sensibles completos.
- [ ] Auditoría activa.
