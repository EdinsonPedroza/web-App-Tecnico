# RESUMEN: Dónde se almacenan los usuarios y cómo verificar MongoDB en Render

## 📍 RESPUESTA DIRECTA A TUS PREGUNTAS

### 1. ¿Dónde se almacenan los usuarios?

Los usuarios se almacenan en **MongoDB**:

- **Sistema de base de datos:** MongoDB (base de datos NoSQL)
- **Ubicación:** Puede ser local (desarrollo) o en la nube (producción)
- **Colección:** `users` (dentro de la base de datos `educando_db`)
- **Código fuente:** `/backend/server.py` líneas 124-262

**Estructura de un usuario en MongoDB:**
```javascript
{
  "id": "user-admin-1",
  "name": "Laura Torres",
  "email": "laura.torres@educando.com",
  "cedula": null,  // Solo para estudiantes
  "password_hash": "$2b$12$...",  // Contraseña encriptada con bcrypt
  "role": "admin",  // estudiante, profesor, admin, o editor
  "active": true,
  "phone": "3002223344",
  "program_id": null,
  "program_ids": [],
  "subject_ids": [],
  "module": null,
  "grupo": null
}
```

### 2. ¿Por qué las credenciales no funcionan?

**La causa MÁS PROBABLE:** MongoDB NO está conectado en Render.

❌ Sin MongoDB conectado = Sin usuarios almacenados = Credenciales no funcionan

### 3. ¿Debería haber una base de datos conectada a Render?

**SÍ, ABSOLUTAMENTE.** Pero hay un detalle importante:

⚠️ **Render NO incluye MongoDB automáticamente en el despliegue.**

Debes:
1. Crear una base de datos MongoDB (recomendado: MongoDB Atlas gratis)
2. Configurar la variable de entorno `MONGO_URL` en Render manualmente
3. Re-desplegar el backend

### 4. ¿Cómo verifico que todo esté bien?

Ver la sección "Verificación Completa" más abajo.

---

## 🚨 DIAGNÓSTICO RÁPIDO

### Paso 1: Revisar los logs del backend en Render

1. Ve a https://dashboard.render.com
2. Selecciona el servicio `educando-backend`
3. Haz clic en la pestaña **"Logs"**

**Busca estos mensajes:**

✅ **SI ESTÁ TODO BIEN:**
```
INFO - Starting application initialization...
INFO - Connecting to MongoDB at: cloud/remote
INFO - MongoDB connection successful
INFO - Datos iniciales creados exitosamente
INFO - Credenciales creadas para 7 usuarios.
INFO - Application startup completed successfully
```

❌ **SI MONGODB NO ESTÁ CONECTADO:**
```
ERROR - Startup failed: ServerSelectionTimeoutError...
ERROR - MongoDB connection failed. Please check your MONGO_URL environment variable.
WARNING - Application started WITHOUT database connection.
```

### Paso 2: Verificar las variables de entorno

1. En Render, ve a `educando-backend` → pestaña **"Environment"**
2. Busca la variable `MONGO_URL`

❌ **Si no existe o está vacía:** ¡Ahí está el problema!
✅ **Si existe:** Verifica que el formato sea correcto:
```
mongodb+srv://usuario:contraseña@cluster.mongodb.net/educando_db?retryWrites=true&w=majority
```

---

## ✅ SOLUCIÓN PASO A PASO

Sigue esta guía completa: **[RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)**

### Resumen rápido (15 minutos):

1. **Crear cuenta en MongoDB Atlas** (gratis)
   - https://www.mongodb.com/cloud/atlas/register

2. **Crear cluster gratuito (M0)**
   - 512MB de almacenamiento (suficiente para empezar)

3. **Crear usuario de base de datos**
   - Usuario: `educando_user` (o el que prefieras)
   - Contraseña: genera una segura

4. **Permitir acceso desde cualquier IP**
   - Network Access → Add IP Address → Allow Access from Anywhere (0.0.0.0/0)

5. **Copiar la connection string**
   ```
   mongodb+srv://educando_user:TuPassword@cluster.mongodb.net/educando_db?retryWrites=true&w=majority
   ```

6. **Configurar en Render**
   - Render Dashboard → educando-backend → Environment
   - Agregar: `MONGO_URL` = tu connection string

7. **Re-desplegar**
   - Manual Deploy → Deploy latest commit
   - Esperar 2-3 minutos

8. **Verificar logs**
   - Debe decir: "MongoDB connection successful"
   - Debe decir: "Credenciales creadas para 7 usuarios"

9. **Probar login**
   - Email: `laura.torres@educando.com`
   - Contraseña: Ver archivo `USUARIOS_Y_CONTRASEÑAS.txt`

---

## 🔍 VERIFICACIÓN COMPLETA

### Opción 1: Verificar desde los logs de Render

**Lo que debes buscar:**

```
# ✅ Conexión exitosa
INFO - MongoDB connection successful

# ✅ Base de datos configurada correctamente
INFO - MongoDB client initialized for database: educando_db

# ✅ Usuarios creados
INFO - Datos iniciales creados exitosamente
INFO - Credenciales creadas para 7 usuarios.

# ✅ Backend funcionando
INFO - Application startup completed successfully
INFO - Application startup complete
INFO - Uvicorn running on http://0.0.0.0:10000
```

### Opción 2: Usar MongoDB Compass (GUI)

1. Descargar: https://www.mongodb.com/try/download/compass
2. Instalar y abrir
3. Conectar usando tu connection string de Atlas
4. Expandir base de datos `educando_db` → colección `users`
5. Deberías ver **7 usuarios**:
   - 1 Editor (carlos.mendez@educando.com)
   - 2 Admins (laura.torres@..., roberto.ramirez@...)
   - 2 Profesores (diana.silva@..., miguel.castro@...)
   - 2 Estudiantes (cédulas: 1001234567, 1002345678)

### Opción 3: Usar el script de verificación

```bash
# Desde tu computadora local
cd backend
pip install motor python-dotenv

# Ejecutar con tu connection string
python verify_mongodb.py "mongodb+srv://user:pass@cluster.mongodb.net/educando_db"
```

El script te mostrará:
- ✅ Estado de la conexión
- ✅ Número de usuarios en la base de datos
- ✅ Lista de todos los usuarios (sin contraseñas)
- ✅ Información del servidor MongoDB

### Opción 4: Probar el endpoint del backend

```bash
# Reemplaza con tu URL de backend en Render
curl https://tu-backend.onrender.com/api/health
```

Debe devolver:
```json
{"status": "healthy"}
```

---

## 📚 ARCHIVOS DE REFERENCIA

### Credenciales de los usuarios
**Archivo:** `USUARIOS_Y_CONTRASEÑAS.txt`

Contiene las credenciales de los 7 usuarios creados automáticamente:
- 1 Editor
- 2 Administradores
- 2 Profesores
- 2 Estudiantes

**Ejemplo:**
- Admin: `laura.torres@educando.com` / Ver archivo para contraseña
- Estudiante: Cédula `1001234567` / Ver archivo para contraseña

### Guía completa de MongoDB en Render
**Archivo:** `RENDER_MONGODB_SETUP.md`

Guía paso a paso de 400+ líneas que cubre:
- ✅ Cómo crear cuenta en MongoDB Atlas
- ✅ Cómo crear y configurar un cluster
- ✅ Cómo obtener la connection string
- ✅ Cómo configurar Render
- ✅ Solución de problemas comunes
- ✅ Cómo verificar que los usuarios existan

### Configuración de Render
**Archivo:** `render.yaml`

Actualizado con comentarios explicativos sobre:
- Por qué Render no incluye MongoDB automáticamente
- Cómo configurar MONGO_URL
- Cómo verificar la conexión en los logs

### Script de verificación
**Archivo:** `backend/verify_mongodb.py`

Script de Python para verificar:
- Conexión a MongoDB
- Existencia de usuarios
- Estado de las colecciones
- Información del servidor

---

## 🎯 CHECKLIST: ¿Todo está configurado?

Marca cada item cuando lo completes:

### Configuración de MongoDB
- [ ] Creé cuenta en MongoDB Atlas
- [ ] Creé cluster gratuito (M0)
- [ ] Creé usuario de base de datos
- [ ] Permití acceso desde 0.0.0.0/0
- [ ] Copié la connection string
- [ ] Reemplacé `<password>` con mi contraseña real
- [ ] Agregué `/educando_db` antes del `?`

### Configuración en Render
- [ ] Configuré variable `MONGO_URL` en backend
- [ ] Re-desplegué el backend
- [ ] Esperé que termine el despliegue (2-3 min)

### Verificación
- [ ] Revisé los logs del backend
- [ ] Vi el mensaje "MongoDB connection successful"
- [ ] Vi el mensaje "Credenciales creadas para 7 usuarios"
- [ ] Probé iniciar sesión con una credencial
- [ ] El login funcionó correctamente

---

## 🆘 PROBLEMAS COMUNES

### Error: "ServerSelectionTimeoutError"

**Causa:** No puede conectarse a MongoDB.

**Soluciones:**
1. Verifica que el cluster esté activo (no en pausa)
2. Permite acceso desde 0.0.0.0/0 en Network Access
3. Espera 2-3 minutos si acabas de crear el cluster
4. Verifica que la connection string sea correcta

### Error: "Authentication failed"

**Causa:** Usuario o contraseña incorrectos en la connection string.

**Soluciones:**
1. Verifica que reemplazaste `<password>` correctamente
2. Si tu contraseña tiene caracteres especiales (@, :, /, ?), encódalos:
   - `@` → `%40`
   - `:` → `%3A`
   - `/` → `%2F`
   - `?` → `%3F`
3. Crea un nuevo usuario con contraseña sin caracteres especiales

### Error: "Credenciales incorrectas" en el login

**Diagnóstico:**

1. **Verifica MongoDB:** Logs del backend deben decir "MongoDB connection successful"
   - ❌ Si no: MongoDB no está conectado → Ver RENDER_MONGODB_SETUP.md
   
2. **Verifica que los usuarios existan:** Logs deben decir "Credenciales creadas para 7 usuarios"
   - ❌ Si no: Algo falló al crear usuarios → Re-desplegar backend
   
3. **Verifica el rol correcto:**
   - Estudiantes: Pestaña "ESTUDIANTE" + cédula
   - Profesores/Admins/Editores: Pestaña "PROFESOR" + email
   
4. **Verifica la contraseña:** Consulta `USUARIOS_Y_CONTRASEÑAS.txt`
   - Las contraseñas distinguen mayúsculas/minúsculas

### El frontend no conecta con el backend

1. En Render → `educando-frontend` → Environment
2. Verifica `REACT_APP_BACKEND_URL`
3. Debe ser la URL del backend (ej: `https://educando-backend.onrender.com`)
4. Si cambiaste algo, re-despliega el frontend

---

## 📞 RECURSOS Y AYUDA

### Documentación oficial
- MongoDB Atlas: https://www.mongodb.com/docs/atlas/
- Render: https://render.com/docs

### Herramientas
- MongoDB Compass (GUI): https://www.mongodb.com/try/download/compass
- MongoDB Shell (CLI): https://www.mongodb.com/try/download/shell

### Archivos del proyecto
- `RENDER_MONGODB_SETUP.md` - Guía completa paso a paso
- `USUARIOS_Y_CONTRASEÑAS.txt` - Credenciales de usuarios
- `backend/verify_mongodb.py` - Script de verificación
- `render.yaml` - Configuración de Render
- `backend/server.py` - Código del backend (líneas 124-683 para auth)

---

## 📝 RESUMEN EJECUTIVO

**Problema:** Credenciales no funcionan en Render.

**Causa raíz:** MongoDB no está conectado.

**Solución:** Configurar MongoDB Atlas (gratis) y conectarlo a Render.

**Tiempo estimado:** 15-20 minutos.

**Archivos clave:**
1. `RENDER_MONGODB_SETUP.md` - Guía completa
2. `USUARIOS_Y_CONTRASEÑAS.txt` - Credenciales
3. `backend/verify_mongodb.py` - Script de verificación

**Verificación exitosa:**
```
✅ MongoDB connection successful
✅ Datos iniciales creados exitosamente  
✅ Credenciales creadas para 7 usuarios
✅ Login funciona con las credenciales del archivo
```

---

**¿Aún tienes problemas?** Comparte los logs del backend en Render para un diagnóstico más específico.

---

*Última actualización: 2026-02-18*
*Documentación creada por: GitHub Copilot*
