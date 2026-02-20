# 📋 TARJETA DE REFERENCIA RÁPIDA - MongoDB en Render

## 🔍 ¿DÓNDE SE ALMACENAN LOS USUARIOS?

```
Sistema:     MongoDB (base de datos NoSQL)
Base de datos: educando_db
Colección:   users
Ubicación:   MongoDB Atlas (nube) o local
Código:      backend/server.py líneas 124-262
```

---

## 🚀 CONFIGURAR MONGODB EN RENDER (5 PASOS)

### 1️⃣ Crear cluster en MongoDB Atlas
```
URL: https://www.mongodb.com/cloud/atlas/register
→ Crear cuenta gratis
→ Build a Database → M0 FREE (512MB)
→ Esperar 1-3 minutos
```

### 2️⃣ Crear usuario de base de datos
```
→ Database Access → Add New Database User
Usuario: educando_user
Contraseña: [genera una segura]
Privilegios: Read and write to any database
```

### 3️⃣ Permitir acceso desde cualquier IP
```
→ Network Access → Add IP Address
→ Allow Access from Anywhere (0.0.0.0/0)
```

### 4️⃣ Obtener connection string
```
→ Database → Connect → Connect your application
→ Driver: Python 3.12
→ Copiar connection string
→ Reemplazar <password> con tu contraseña
→ Agregar /educando_db antes del ?

Ejemplo correcto:
mongodb+srv://educando_user:MiPass123@cluster.abc.mongodb.net/educando_db?retryWrites=true&w=majority
```

### 5️⃣ Configurar en Render
```
→ Render Dashboard → educando-backend → Environment
→ Agregar variable: MONGO_URL = [tu connection string]
→ Save Changes
→ Manual Deploy → Deploy latest commit
→ Esperar 2-3 minutos
```

---

## ✅ VERIFICAR QUE FUNCIONE

### En los logs de Render:
```
✅ "MongoDB connection successful"
✅ "Datos iniciales creados exitosamente"
✅ "Credenciales creadas para 7 usuarios"
```

### Probar login:
```
ROL: Profesor (pestaña)
EMAIL: laura.torres@educando.com
PASS: [Ver USUARIOS_Y_CONTRASEÑAS.txt]
```

---

## 🔧 COMANDOS ÚTILES

### Verificar conexión (local):
```bash
pip install motor python-dotenv
python backend/verify_mongodb.py "mongodb+srv://..."
```

### Ver usuarios en MongoDB Compass:
```
1. Descargar: https://www.mongodb.com/try/download/compass
2. Conectar con tu connection string
3. educando_db → users → Ver 7 usuarios
```

### Probar backend directamente:
```bash
curl https://tu-backend.onrender.com/api/health
# Debe devolver: {"status": "healthy"}
```

---

## 🆘 ERRORES COMUNES

| Error | Causa | Solución |
|-------|-------|----------|
| `ServerSelectionTimeoutError` | No puede conectar a MongoDB | 1. Verifica Network Access (0.0.0.0/0)<br>2. Cluster debe estar activo<br>3. Connection string correcta |
| `Authentication failed` | Usuario/contraseña incorrectos | 1. Verifica que reemplazaste `<password>`<br>2. Codifica caracteres especiales (%40, %3A) |
| `Credenciales incorrectas` (login) | MongoDB no conectado | 1. Verifica logs: "MongoDB connection successful"<br>2. Re-desplegar backend |
| Rol incorrecto | Pestaña equivocada | Estudiantes: ESTUDIANTE + cédula<br>Profesores/Admins: PROFESOR + email |

---

## 👥 USUARIOS POR DEFECTO (7 TOTAL)

```
📝 Editor (1):
   carlos.mendez@educando.com [pestaña PROFESOR]

👑 Admins (2):
   laura.torres@educando.com [pestaña PROFESOR]
   roberto.ramirez@educando.com [pestaña PROFESOR]

👨‍🏫 Profesores (2):
   diana.silva@educando.com [pestaña PROFESOR]
   miguel.castro@educando.com [pestaña PROFESOR]

🎓 Estudiantes (2):
   1001234567 [pestaña ESTUDIANTE]
   1002345678 [pestaña ESTUDIANTE]

⚠️ Ver USUARIOS_Y_CONTRASEÑAS.txt para las contraseñas
```

---

## 📚 ARCHIVOS IMPORTANTES

```
RENDER_MONGODB_SETUP.md          → Guía completa paso a paso (400+ líneas)
RESUMEN_USUARIOS_Y_MONGODB.md    → Resumen ejecutivo con checklist
USUARIOS_Y_CONTRASEÑAS.txt       → Credenciales de los 7 usuarios
backend/verify_mongodb.py        → Script de verificación de conexión
render.yaml                      → Configuración de Render
backend/server.py (124-683)      → Código de autenticación y usuarios
```

---

## 🎯 CHECKLIST RÁPIDO

```
[ ] Creé cuenta en MongoDB Atlas
[ ] Creé cluster M0 (gratis)
[ ] Creé usuario de BD
[ ] Permití 0.0.0.0/0 en Network Access
[ ] Copié connection string correctamente
[ ] Reemplacé <password> con contraseña real
[ ] Agregué /educando_db antes del ?
[ ] Configuré MONGO_URL en Render
[ ] Re-desplegué el backend
[ ] Verifiqué logs: "MongoDB connection successful"
[ ] Probé login con credencial de prueba
[ ] ¡Funcionó! ✅
```

---

## 🔗 ENLACES IMPORTANTES

```
MongoDB Atlas:        https://www.mongodb.com/cloud/atlas
Render Dashboard:     https://dashboard.render.com
MongoDB Compass:      https://www.mongodb.com/try/download/compass
MongoDB Shell:        https://www.mongodb.com/try/download/shell
Repo GitHub:          https://github.com/EdinsonPedroza/web-App-Tecnico
```

---

## 💡 FORMATO DE MONGO_URL

### ✅ CORRECTO:
```
mongodb+srv://user:Pass123@cluster.abc.mongodb.net/educando_db?retryWrites=true&w=majority
           ^^^^  ^^^^^^^  ^^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^
           user  password      host               database
```

### ❌ INCORRECTO:
```
# Sin reemplazar <password>
mongodb+srv://user:<password>@cluster.abc.mongodb.net/educando_db

# Sin /educando_db
mongodb+srv://user:Pass123@cluster.abc.mongodb.net/?retryWrites=true

# Con espacios
mongodb+srv://user:Pass123@cluster.abc.mongodb.net/educando_db ?retryWrites=true
```

---

## 🔐 CARACTERES ESPECIALES EN CONTRASEÑAS

Si tu contraseña tiene estos caracteres, encódalos en la URL:

```
@  → %40      Ejemplo: Pass@123 → Pass%40123
:  → %3A               Pass:123 → Pass%3A123
/  → %2F               Pass/123 → Pass%2F123
?  → %3F               Pass?123 → Pass%3F123
#  → %23               Pass#123 → Pass%23123
```

**O mejor:** Crea un nuevo usuario con contraseña sin caracteres especiales.

---

## 🚨 DIAGNÓSTICO EN 30 SEGUNDOS

```
1. Render → educando-backend → Logs
2. ¿Dice "MongoDB connection successful"?
   ✅ SÍ → MongoDB conectado, problema es otro
   ❌ NO → MongoDB NO conectado, seguir guía

3. Si NO está conectado:
   → Render → educando-backend → Environment
   → ¿Existe MONGO_URL?
      ❌ NO → Agregar MONGO_URL (ver guía)
      ✅ SÍ → Verificar formato (ver arriba)
   
4. Después de configurar MONGO_URL:
   → Manual Deploy → Deploy latest commit
   → Esperar 2-3 min
   → Volver a step 1
```

---

*Guarda esta tarjeta para referencia rápida*
*Última actualización: 2026-02-18*
