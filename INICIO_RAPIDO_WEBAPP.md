# 🚀 Inicio Rápido - Base de Datos webApp Configurada

## ✅ ¡Todo Está Configurado!

Tu aplicación ya está conectada a la base de datos **webApp** en MongoDB Atlas (Cluster0).

## ⚡ Pasos para Iniciar (5 minutos)

### 1. Configurar Acceso en MongoDB Atlas (IMPORTANTE)

🔓 **Permitir conexión desde cualquier IP:**

1. Ve a https://cloud.mongodb.com/
2. Inicia sesión con tu cuenta
3. En el menú lateral → **Network Access**
4. Click **"+ ADD IP ADDRESS"**
5. Selecciona **"ALLOW ACCESS FROM ANYWHERE"** (0.0.0.0/0)
6. Click **"Confirm"**
7. ⏱️ Espera 1-2 minutos

✅ Listo! Ahora tu aplicación puede conectarse.

### 2. Iniciar la Aplicación

#### Con Docker (Más Fácil):

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

### 3. Iniciar Sesión

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

## 🎉 Qué Se Creará Automáticamente

Al iniciar la aplicación por primera vez:

✅ **Base de datos**: webApp  
✅ **Collections**: users, programs, subjects, courses, activities, grades, submissions, App  
✅ **7 Usuarios**: 1 editor, 2 admins, 2 profesores, 2 estudiantes  
✅ **3 Programas académicos** con todas sus materias  
✅ **1 Curso de ejemplo** con actividades  

## 🔍 Verificar que Todo Funciona

### Opción 1: Logs del Backend

Busca estos mensajes al iniciar:

```
✅ MongoDB connection successful
✅ Credenciales creadas para 7 usuarios
✅ Application startup completed successfully
```

### Opción 2: MongoDB Atlas

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

**Solución**: Revisa el Paso 1 - Configurar Network Access

### "Authentication failed"

**Solución**: 
1. Ve a MongoDB Atlas → **Database Access**
2. Verifica el usuario `insonest2106_db_user`
3. Debe tener rol "Read and write to any database"

### No puedo iniciar sesión

**Solución**: 
1. Revisa los logs del backend
2. Debe aparecer: "Credenciales creadas para 7 usuarios"
3. Si no aparece, verifica la conexión a MongoDB

## 📚 Más Información

- 📖 [Guía Completa de Configuración](./CONFIGURACION_MONGODB.md)
- 📋 [Lista de Todos los Usuarios](./USUARIOS_Y_CONTRASEÑAS.txt)
- 🛠️ [README Principal](./README.md)

## 🆘 Necesitas Ayuda?

Si algo no funciona:

1. **Primero**: Lee [CONFIGURACION_MONGODB.md](./CONFIGURACION_MONGODB.md)
2. **Logs**: Revisa los logs del backend para ver el error específico
3. **MongoDB**: Verifica en MongoDB Atlas que el cluster esté activo

---

**¡Listo para empezar!** 🎉

Todo está configurado. Solo necesitas permitir el acceso en MongoDB Atlas (Paso 1) y tu aplicación funcionará perfectamente.
