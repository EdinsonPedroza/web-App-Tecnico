# ✅ Checklist rápido: ¿tu despliegue quedó bien?

Ya tienes el frontend, backend y MongoDB desplegados. Sigue estos pasos cortos para validar que todo está correcto y qué hacer después.

> ⚠️ **Advertencia crítica de seguridad:** Las credenciales seed (`admin@educando.com / admin123`) son públicas y solo deben usarse en un entorno local/sandbox sin acceso externo. No las uses en un despliegue público; crea credenciales específicas para el entorno y desactiva las seed antes de abrir el acceso.

> 🔐 **JWT_SECRET obligatorio:** genera un secreto aleatorio de al menos 32 bytes (= 64 caracteres hex con `openssl rand -hex 32`) antes de exponer el backend. No reutilices secretos de otros entornos ni lo dejes vacío.

**Credenciales seed (solo para validar en entorno aislado)**
- `SEED_ADMIN_EMAIL=admin@educando.com`
- `SEED_ADMIN_PASSWORD=admin123`

## Seguridad obligatoria (antes de dar acceso)
- Genera y configura `JWT_SECRET` (>= 32 bytes aleatorios) durante el despliegue inicial.
- Crea credenciales propias para admin en el entorno y desactiva/rota las seed antes de permitir acceso público.
- Cambia inmediatamente la contraseña al usar cualquier credencial seed para validar.

## 1) Ten a la mano
- URL pública del **frontend** (ej: `https://web-app-tecnico-production.up.railway.app`)
- URL pública del **backend** (Networking del servicio backend)
- Variables en backend: `MONGO_URL`, `DB_NAME`, `JWT_SECRET` (debe estar configurado según la sección **Seguridad obligatoria**).
- Credenciales iniciales para probar: las seed listadas arriba (solo en entorno privado); antes de hacerlo público aplica la sección de seguridad.

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
3) **Frontend y sesión:** abre la URL del frontend, inicia sesión con las credenciales seed indicadas arriba, verifica que carga el dashboard sin errores y cambia la contraseña en cuanto ingreses (ver sección **Seguridad obligatoria**).
4) **Datos en Mongo:** en Railway → servicio MongoDB → “Data” o “Connect”, ejecuta:
   ```js
   db.users.findOne({ email: "admin@educando.com" })
   ```
   Si devuelve un documento, los datos iniciales se cargaron bien.
5) **Checklist de seguridad:** confirma que aplicaste la sección **Seguridad obligatoria** (JWT_SECRET configurado y credenciales seed reemplazadas) antes de dejar el entorno accesible.

## 3) Qué hacer después
- Comparte la URL del frontend con tu equipo para pruebas finales.
- Opcional: añade dominio propio en Railway → Frontend → Networking → Custom Domain.
- Descarga un backup manual de MongoDB desde Railway (tab Backups o “Create Backup”).
- Crea un segundo usuario admin con tu correo real y desactiva o cambia de inmediato la cuenta por defecto (ver sección de seguridad).

## 4) Si algo falla
- Revisa que las variables del backend estén exactas (`MONGO_URL`, `DB_NAME`, `JWT_SECRET`).
- Mira los logs en cada servicio (tab **Logs** en Railway) y redeploy si ves errores de build.
- Asegúrate de que el frontend apunta a la URL correcta del backend (`REACT_APP_API_URL`).
