# 🚀 Inicio Rápido - Base de Datos webApp

## ✅ Todo Está Listo

Tu aplicación está configurada para conectarse a la base de datos **webApp** en MongoDB Atlas (Cluster0).

## ⚡ Configuración en 3 Pasos (5 minutos)

### Paso 1: Configurar Credenciales (2 minutos)

Elige UNA de estas opciones:

#### Opción A: Script Automático (Más Fácil) ⭐

```bash
./configurar_mongodb.sh
```

El script te preguntará por tu MongoDB URL y nombre de base de datos.

#### Opción B: Variables de Entorno

**Nota**: Reemplaza `USUARIO:PASSWORD` con tus credenciales reales (ver `CREDENCIALES_PRIVADAS.md` si tienes acceso)

**Linux/Mac:**
```bash
export MONGO_URL="mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0"
export DB_NAME="webApp"
```

**Windows (PowerShell):**
```powershell
$env:MONGO_URL="mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0"
$env:DB_NAME="webApp"
```

**Windows (CMD):**
```cmd
set MONGO_URL=mongodb+srv://USUARIO:PASSWORD@cluster0.avzgmr5.mongodb.net/webApp?appName=Cluster0
set DB_NAME=webApp
```

### Paso 2: Configurar MongoDB Atlas (2 minutos)

🔓 **Permitir conexión desde cualquier IP:**

1. Ve a https://cloud.mongodb.com/
2. Inicia sesión con tu cuenta
3. En el menú lateral → **Network Access**
4. Click **"+ ADD IP ADDRESS"**
5. Selecciona **"ALLOW ACCESS FROM ANYWHERE"** (0.0.0.0/0)
6. Click **"Confirm"**
7. ⏱️ Espera 1-2 minutos

### Paso 3: Iniciar la Aplicación (1 minuto)

#### Con Docker (Recomendado):

```bash
docker compose -f docker-compose.dev.yml up --build
```

Abre: http://localhost:3000

#### Sin Docker (Python + Node):

**Terminal 1 - Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm install
npm start
```

Abre: http://localhost:3000

## 🔍 Verificar la Configuración

Antes de iniciar la aplicación, verifica que todo esté bien:

```bash
python verificar_webapp.py
```

Deberías ver: **"✅ CONEXIÓN EXITOSA!"**

## 🎉 Iniciar Sesión

Usa cualquiera de estas credenciales:

**Admin** (Pestaña PROFESOR):
- Email: `laura.torres@educando.com`
- Password: `Admin2026*LT`

**Profesor** (Pestaña PROFESOR):
- Email: `diana.silva@educando.com`
- Password: `Profe2026*DS`

**Estudiante** (Pestaña ESTUDIANTE):
- Cédula: `1001234567`
- Password: `Estud2026*SM`

## 🎊 Qué Se Creará Automáticamente

Al iniciar la aplicación por primera vez:

✅ **Base de datos**: webApp  
✅ **Collections**: users, programs, subjects, courses, activities, grades, submissions, App  
✅ **7 Usuarios**: 1 editor, 2 admins, 2 profesores, 2 estudiantes  
✅ **3 Programas académicos** con todas sus materias  
✅ **1 Curso de ejemplo** con actividades  

## 🔍 Verificar que Todo Funciona

### En los Logs del Backend

Busca estos mensajes al iniciar:

```
✅ MongoDB connection successful
✅ Credenciales creadas para 7 usuarios
✅ Application startup completed successfully
```

### En MongoDB Atlas

1. Ve a MongoDB Atlas → **Database** → **Browse Collections**
2. Selecciona la base de datos **webApp**
3. Deberías ver:
   - `users` con 7 documentos
   - `programs` con 3 documentos
   - `subjects` con ~20 documentos
   - `courses` con 1 documento
   - `App` (vacía, como solicitaste)

## ❌ Problemas Comunes

### "Cannot connect to MongoDB"

**Solución**: 
1. Revisa el Paso 2 - Configurar Network Access
2. Espera 2 minutos después de configurarlo

### "MONGO_URL not configured"

**Solución**: 
1. Vuelve al Paso 1
2. Asegúrate de ejecutar el script o configurar las variables

### "Authentication failed"

**Solución**: 
1. Ve a MongoDB Atlas → **Database Access**
2. Verifica tu usuario de base de datos
3. Debe tener rol "Read and write to any database"

### No puedo iniciar sesión en la app

**Solución**: 
1. Revisa los logs del backend
2. Debe aparecer: "Credenciales creadas para 7 usuarios"
3. Si no aparece, verifica la conexión a MongoDB

## 📚 Más Información

- 📖 [Guía Completa de Configuración](./CONFIGURACION_MONGODB.md)
- 🛠️ [README Principal](./README.md)

## 🎯 Resumen Rápido

```bash
# 1. Configurar credenciales
./configurar_mongodb.sh

# 2. Configurar MongoDB Atlas (en navegador)
# https://cloud.mongodb.com/ → Network Access → Allow from anywhere

# 3. Verificar
python verificar_webapp.py

# 4. Iniciar
docker compose -f docker-compose.dev.yml up --build
```

---

**¡Listo para empezar!** 🎉

Si tienes problemas, revisa la [Guía Completa](./CONFIGURACION_MONGODB.md) para más detalles.
