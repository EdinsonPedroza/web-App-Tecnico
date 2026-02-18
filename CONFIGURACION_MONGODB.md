# Configuración MongoDB - Base de Datos webApp

## ✅ Configuración Completada

Se ha configurado la aplicación para conectarse a tu base de datos MongoDB Atlas:

### Detalles de Conexión

- **Cluster**: Cluster0
- **Base de datos**: webApp
- **Collection**: App (se creará automáticamente)
- **Connection String**: Configurado en `backend/.env`

### Archivos Modificados

1. **`backend/.env`**
   - Se agregó la variable `MONGO_URL` con tu connection string
   - Se cambió `DB_NAME` de "test_database" a "webApp"

## 🔧 Configuración en MongoDB Atlas

Para que la conexión funcione correctamente, necesitas configurar el acceso en MongoDB Atlas:

### Paso 1: Verificar el Cluster

1. Ve a [MongoDB Atlas](https://cloud.mongodb.com/)
2. Inicia sesión con tu cuenta
3. Verifica que el **Cluster0** esté activo (estado verde)

### Paso 2: Configurar Network Access (IMPORTANTE)

La causa más común de errores de conexión es la restricción de IP. Sigue estos pasos:

1. En MongoDB Atlas, ve al menú lateral → **Network Access**
2. Click en **"+ ADD IP ADDRESS"**
3. Selecciona **"ALLOW ACCESS FROM ANYWHERE"** (0.0.0.0/0)
   - Esto permite que tu aplicación se conecte desde cualquier IP
   - Para producción, puedes restringir las IPs específicas más tarde
4. Click en **"Confirm"**
5. Espera 1-2 minutos para que los cambios se apliquen

### Paso 3: Verificar el Usuario de Base de Datos

1. En MongoDB Atlas, ve a **Database Access**
2. Verifica que existe el usuario: `insonest2106_db_user`
3. Asegúrate que tiene rol **"Read and write to any database"** o **"Atlas admin"**
4. Si no existe o no tiene permisos, créalo/edítalo:
   - Username: `insonest2106_db_user`
   - Password: (la que configuraste)
   - Database User Privileges: **"Read and write to any database"**

## 🚀 Qué Hará la Aplicación al Iniciar

Cuando la aplicación se conecte exitosamente, automáticamente:

1. ✅ Creará la base de datos **webApp** (si no existe)
2. ✅ Creará las siguientes colecciones:
   - `users` - Usuarios del sistema (estudiantes, profesores, admins)
   - `programs` - Programas académicos
   - `subjects` - Materias de cada programa
   - `courses` - Cursos activos
   - `activities` - Actividades de cada curso
   - `grades` - Calificaciones de estudiantes
   - `submissions` - Entregas de actividades
   - `App` - Collection vacía (como solicitaste)

3. ✅ Creará usuarios iniciales:
   - 1 Editor
   - 2 Administradores
   - 2 Profesores
   - 2 Estudiantes

4. ✅ Creará 3 programas académicos con sus materias:
   - Técnico en Asistencia Administrativa
   - Técnico Laboral en Atención a la Primera Infancia
   - Técnico en Seguridad y Salud en el Trabajo

5. ✅ Creará un curso de ejemplo con actividades

## 📋 Usuarios de Prueba

Una vez que la aplicación inicie correctamente, podrás iniciar sesión con:

### Administradores (Pestaña PROFESOR)
- **Email**: `laura.torres@educando.com`
- **Password**: `Admin2026*LT`

### Profesores (Pestaña PROFESOR)
- **Email**: `diana.silva@educando.com`
- **Password**: `Profe2026*DS`

### Estudiantes (Pestaña ESTUDIANTE)
- **Cédula**: `1001234567`
- **Password**: `Estud2026*SM`

## 🧪 Cómo Probar la Conexión

### Opción 1: Usando Docker (Recomendado)

```bash
cd /home/runner/work/web-App-Tecnico/web-App-Tecnico
docker compose -f docker-compose.dev.yml up --build
```

Luego abre: http://localhost:3000

### Opción 2: Desarrollo Local con Python

```bash
cd backend
pip install -r requirements.txt
python verify_mongodb.py
```

Si ves el mensaje **"✅ Conexión exitosa!"**, la configuración es correcta.

### Opción 3: Iniciar el Servidor Directamente

```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

Busca en los logs:
```
✅ MongoDB connection successful
✅ Credenciales creadas para 7 usuarios
```

## 🔒 Seguridad

⚠️ **IMPORTANTE**: El archivo `backend/.env` ahora contiene credenciales sensibles.

### Para Desarrollo Local:
- El archivo `.env` está en `.gitignore`, así que no se subirá a GitHub
- Está bien tener las credenciales aquí para desarrollo

### Para Producción (Railway, Render, etc.):
**NO uses el archivo .env en producción**. En su lugar:

1. Ve al dashboard de tu plataforma (Railway/Render)
2. Agrega las variables de entorno:
   - `MONGO_URL`: `mongodb+srv://insonest2106_db_user:HLDVMjvKWHMg4Dg2@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0`
   - `DB_NAME`: `webApp`
   - `CORS_ORIGINS`: Tu dominio de frontend (ej: `https://tu-app.render.com`)
   - `JWT_SECRET`: Una clave secreta segura (genera una nueva)

## 🐛 Solución de Problemas

### Error: "No address associated with hostname"

**Causa**: Network Access no configurado en MongoDB Atlas  
**Solución**: Sigue el Paso 2 de esta guía (ALLOW ACCESS FROM ANYWHERE)

### Error: "Authentication failed"

**Causa**: Usuario o contraseña incorrectos  
**Solución**: 
1. Ve a MongoDB Atlas → Database Access
2. Edita el usuario `insonest2106_db_user`
3. Resetea la contraseña si es necesario
4. Actualiza `backend/.env` con la nueva contraseña

### Error: "ServerSelectionTimeoutError"

**Causa**: El cluster no está accesible  
**Solución**:
1. Verifica que el cluster esté activo en MongoDB Atlas
2. Espera 2-3 minutos después de configurar Network Access
3. Verifica tu conexión a internet

### La aplicación inicia pero no puedo iniciar sesión

**Causa**: Los usuarios no se crearon  
**Solución**:
1. Ve a MongoDB Atlas → Browse Collections
2. Verifica que exista la colección `users` con 7 documentos
3. Si no existe, elimina la base de datos y reinicia la aplicación

## 📚 Recursos Adicionales

- [Documentación MongoDB Atlas](https://docs.atlas.mongodb.com/)
- [Guía de Conexión String](https://docs.mongodb.com/manual/reference/connection-string/)
- [README del Proyecto](./README.md)
- [Guía de Usuarios y Contraseñas](./USUARIOS_Y_CONTRASEÑAS.txt)

## ✨ Estado Actual

✅ **Backend configurado** con la connection string correcta  
✅ **Base de datos configurada** (webApp)  
✅ **Inicialización automática** lista para crear datos  
⏳ **Pendiente**: Configurar Network Access en MongoDB Atlas (acción del usuario)

Una vez que configures Network Access en MongoDB Atlas, todo funcionará automáticamente.
