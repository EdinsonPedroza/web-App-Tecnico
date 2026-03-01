# Política de seguridad

## Reportar vulnerabilidades

Si descubres una vulnerabilidad de seguridad en este proyecto, por favor **no abras un issue público**.  
En su lugar, envía un correo a la dirección de contacto del equipo técnico de la Corporación Social Educando con:

- Descripción de la vulnerabilidad
- Pasos para reproducirla
- Impacto potencial estimado

Responderemos en un plazo máximo de 5 días hábiles.

---

## No comitas credenciales

- Los archivos `.env`, `backend/.env` y `frontend/.env` están excluidos del repositorio mediante `.gitignore`.  
  **Nunca** elimines estas entradas del `.gitignore`.
- Usa siempre archivos `.env.example` (sin valores reales) para documentar las variables necesarias.
- Si por error se commitieron credenciales reales, rótalas de inmediato (MongoDB, AWS, JWT secret, etc.).

---

## Recomendaciones de seguridad para el despliegue

| Área | Recomendación |
|---|---|
| **JWT_SECRET** | Genera con `openssl rand -hex 32`. Nunca uses valores por defecto. Rota periódicamente; ten en cuenta que la rotación invalida todas las sesiones activas y obliga a los usuarios a re-autenticarse. |
| **MongoDB** | Usa un usuario con mínimos privilegios (`readWrite` sobre la BD de la app). Activa MFA en Atlas. |
| **AWS S3** | Crea un usuario IAM dedicado con política de mínimo privilegio. Nunca uses las credenciales root. |
| **CORS_ORIGINS** | Lista solo los dominios autorizados. Nunca uses `*` en producción. |
| **HTTPS** | Render provee TLS automático. Asegúrate de que todo el tráfico use HTTPS. |
| **Dependencias** | Ejecuta `npm audit` y `pip-audit` periódicamente para detectar vulnerabilidades en dependencias. |
| **Logs** | No registres contraseñas, tokens ni datos personales en los logs. |
