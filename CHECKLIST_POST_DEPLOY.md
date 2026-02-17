# ✅ Checklist rápido: ¿tu despliegue quedó bien?

Ya tienes el frontend, backend y MongoDB desplegados. Sigue estos pasos cortos para validar que todo está correcto y qué hacer después.

> ⚠️ **Advertencia crítica de seguridad:** Las credenciales seed (`admin@educando.com / admin123`) son públicas y solo deben usarse en un entorno aislado para la primera verificación. Cámbialas o desactívalas inmediatamente después del primer inicio de sesión antes de abrir el acceso a otros usuarios.

## 1) Ten a la mano
- URL pública del **frontend** (ej: `https://web-app-tecnico-production.up.railway.app`)
- URL pública del **backend** (Networking del servicio backend)
- Variables en backend: `MONGO_URL`, `DB_NAME`, `JWT_SECRET` (configura un secreto aleatorio de al menos 32 caracteres **antes** de abrir el entorno; no dejes el valor vacío ni reutilices secretos de otros entornos).
- Credenciales iniciales para probar (solo si dejaste los datos seed por defecto): `admin@educando.com / admin123`. Úsalas solo en un entorno privado para validar; antes de hacerlo público crea credenciales nuevas y desactiva las seed.

## 2) Verificación en 5 minutos
1) **Estado en Railway:** abre el proyecto y confirma que MongoDB, backend y frontend están en verde/“Active”. Si alguno está en rojo, presiona **Restart** o **Redeploy**.
2) **Backend responde:** en tu terminal ejecuta (cambia la URL por la tuya):
   ```bash
   # Solo para validar en entorno aislado; rota la contraseña inmediatamente después.
   curl -X POST "https://TU-BACKEND.up.railway.app/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@educando.com","password":"admin123"}'
   ```
   Debes recibir un `access_token` en JSON. Si falla, revisa variables y logs del backend.
3) **Frontend y sesión:** abre la URL del frontend, inicia sesión con `admin@educando.com / admin123`, verifica que carga el dashboard sin errores y cambia la contraseña antes de continuar con cualquier otra acción.
4) **Datos en Mongo:** en Railway → servicio MongoDB → “Data” o “Connect”, ejecuta:
   ```js
   db.users.findOne({ email: "admin@educando.com" })
   ```
   Si devuelve un documento, los datos iniciales se cargaron bien.
5) **Seguridad mínima:** confirma que ya usas un `JWT_SECRET` de al menos 32 caracteres generado localmente (ej. `openssl rand -hex 32`) y que el admin tiene contraseña nueva. Tras crear tu usuario admin propio, desactiva o cambia de inmediato las credenciales seed.

## 3) Qué hacer después
- Comparte la URL del frontend con tu equipo para pruebas finales.
- Opcional: añade dominio propio en Railway → Frontend → Networking → Custom Domain.
- Descarga un backup manual de MongoDB desde Railway (tab Backups o “Create Backup”).
- Crea un segundo usuario admin con tu correo real y desactiva o cambia de inmediato la cuenta por defecto.

## 4) Si algo falla
- Revisa que las variables del backend estén exactas (`MONGO_URL`, `DB_NAME`, `JWT_SECRET`).
- Mira los logs en cada servicio (tab **Logs** en Railway) y redeploy si ves errores de build.
- Asegúrate de que el frontend apunta a la URL correcta del backend (`REACT_APP_API_URL`).
