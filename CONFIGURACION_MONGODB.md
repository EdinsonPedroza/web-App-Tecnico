# Configuración MongoDB - Base de Datos webApp

## ✅ Resumen

La aplicación está lista para conectarse a tu base de datos **webApp** en MongoDB Atlas (Cluster0).

### 🔒 Seguridad Importante

**Este repositorio es PÚBLICO.** Por seguridad, las credenciales de MongoDB **NO están incluidas** en los archivos rastreados por Git.

Debes configurar las credenciales localmente usando una de estas opciones:

## 🚀 Opción 1: Script Automático (Más Fácil)

Usa el script de configuración que crea un archivo seguro `.env.local`:

```bash
./configurar_mongodb.sh
```

El script te preguntará por tu connection string y creará `backend/.env.local` (que NO se sube a Git).

## 🔧 Opción 2: Variables de Entorno del Sistema

Configura las variables antes de iniciar la aplicación:

**Nota**: Las credenciales reales están en el archivo `CREDENCIALES_PRIVADAS.md` (no incluido en el repositorio público)

**Linux/Mac:**
```bash
export MONGO_URL="mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0"
export DB_NAME="webApp"
cd backend
uvicorn server:app --reload
```

**Windows (PowerShell):**
```powershell
$env:MONGO_URL="mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0"
$env:DB_NAME="webApp"
cd backend
uvicorn server:app --reload
```

**Windows (CMD):**
```cmd
set MONGO_URL=mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0
set DB_NAME=webApp
cd backend
uvicorn server:app --reload
```

## 📝 Opción 3: Crear .env.local Manualmente

Crea un archivo `backend/.env.local` (este archivo NO se sube a Git):

```bash
# backend/.env.local
MONGO_URL="mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0"
DB_NAME="webApp"
CORS_ORIGINS="*"
```

**Reemplaza `USUARIO:PASSWORD` con tus credenciales reales** (ver `CREDENCIALES_PRIVADAS.md` si tienes acceso)

## 📊 Detalles de Conexión

- **Cluster**: Cluster0
- **Base de datos**: webApp
- **Collection**: App (se creará automáticamente)
- **Credenciales**: Ver archivo `CREDENCIALES_PRIVADAS.md` (no incluido en repositorio público)

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
2. Verifica que existe tu usuario de base de datos
3. Asegúrate que tiene rol **"Read and write to any database"** o **"Atlas admin"**
4. Si no existe o no tiene permisos, créalo/edítalo con los permisos necesarios

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

### Opción 1: Verificar con el Script

```bash
python verificar_webapp.py
```

Si ves el mensaje **"✅ Conexión exitosa!"**, la configuración es correcta.

### Opción 2: Usando Docker (Recomendado)

```bash
docker compose -f docker-compose.dev.yml up --build
```

Luego abre: http://localhost:3000

### Opción 3: Desarrollo Local con Python

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

## 🔒 Seguridad para Producción

### Para Despliegue en Railway, Render, Heroku, etc.

**NO uses archivos .env en producción**. Configura las variables de entorno en tu plataforma:

**Railway:**
```
Settings → Variables → Add Variable
MONGO_URL=mongodb+srv://...
DB_NAME=webApp
```

**Render:**
```
Environment → Add Environment Variable
MONGO_URL=mongodb+srv://...
DB_NAME=webApp
```

**Heroku:**
```
Settings → Config Vars → Add
MONGO_URL=mongodb+srv://...
DB_NAME=webApp
```

## 🐛 Solución de Problemas

### Error: "No address associated with hostname"

**Causa**: Network Access no configurado en MongoDB Atlas  
**Solución**: Sigue el Paso 2 de esta guía (ALLOW ACCESS FROM ANYWHERE)

### Error: "Authentication failed"

**Causa**: Usuario o contraseña incorrectos  
**Solución**: 
1. Ve a MongoDB Atlas → Database Access
2. Edita tu usuario de base de datos
3. Resetea la contraseña si es necesario
4. Actualiza tu configuración local

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
- [Guía de Connection String](https://docs.mongodb.com/manual/reference/connection-string/)
- [README del Proyecto](./README.md)
- [Inicio Rápido](./INICIO_RAPIDO_WEBAPP.md)

## ✨ Checklist

- [ ] Configurar credenciales localmente (Opción 1, 2 o 3)
- [ ] Configurar Network Access en MongoDB Atlas
- [ ] Verificar que el usuario tenga permisos correctos
- [ ] Ejecutar el script de verificación
- [ ] Iniciar la aplicación
- [ ] Verificar que se crearon los usuarios y colecciones
- [ ] Probar el inicio de sesión

Una vez completado el checklist, ¡todo funcionará perfectamente! 🎉
