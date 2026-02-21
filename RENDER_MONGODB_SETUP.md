# Guía: Base de Datos MongoDB en Render - Plataforma Educando

## 📌 RESPUESTA A TU PROBLEMA

### ¿Dónde se almacenan los usuarios?

Los usuarios se almacenan en **MongoDB**, específicamente en:
- **Base de datos:** MongoDB (puede ser local o en la nube)
- **Colección:** `users`
- **Ubicación del código:** `backend/server.py` líneas 124-262

### ¿Por qué las credenciales no funcionan?

**La causa más probable es que MongoDB NO ESTÁ CONECTADO en Render.**

Render NO incluye MongoDB automáticamente. Debes:
1. Crear una base de datos MongoDB (usando MongoDB Atlas u otro servicio)
2. Configurar la variable de entorno `MONGO_URL` en Render
3. Verificar que la conexión funcione

---

## 🔍 VERIFICAR SI MONGODB ESTÁ CONECTADO EN RENDER

### Paso 1: Ver los logs del backend en Render

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Selecciona el servicio `educando-backend`
3. Haz clic en la pestaña **"Logs"**
4. Busca estos mensajes:

**✅ Si MongoDB está conectado correctamente, verás:**
```
INFO - Starting application initialization...
INFO - Connecting to MongoDB at: cloud/remote
INFO - MongoDB connection successful
INFO - Datos iniciales creados exitosamente
INFO - Credenciales creadas para 7 usuarios.
INFO - Application startup completed successfully
```

**❌ Si MongoDB NO está conectado, verás:**
```
ERROR - Startup failed: ...
ERROR - MongoDB connection failed. Please check your MONGO_URL environment variable.
WARNING - Application started WITHOUT database connection.
```

### Paso 2: Verificar las variables de entorno

1. En Render, ve a tu servicio `educando-backend`
2. Haz clic en **"Environment"**
3. Verifica que existe la variable `MONGO_URL`

**❌ Si NO existe o está vacía:** ¡Ese es tu problema!
**✅ Si existe:** Verifica que el formato sea correcto (ver más abajo)

---

## 🚀 SOLUCIÓN: CONFIGURAR MONGODB EN RENDER

Render no proporciona MongoDB directamente. Tienes 2 opciones:

### Opción 1: MongoDB Atlas (RECOMENDADO - Gratis hasta 512MB)

MongoDB Atlas es el servicio oficial de MongoDB en la nube, con un plan gratuito generoso.

#### Paso 1: Crear cuenta en MongoDB Atlas

1. Ve a: https://www.mongodb.com/cloud/atlas/register
2. Crea una cuenta gratuita (puedes usar tu cuenta de Google/GitHub)
3. Inicia sesión

#### Paso 2: Crear un Cluster (Base de datos)

1. En el dashboard, haz clic en **"Build a Database"**
2. Selecciona **"M0 - FREE"** (512MB, perfecto para empezar)
3. Elige un proveedor de nube:
   - **AWS** (recomendado)
   - Región: Selecciona la más cercana (ej: `us-east-1` para Norteamérica)
4. Nombre del cluster: `educando-cluster` (o el que prefieras)
5. Haz clic en **"Create"**
6. Espera 1-3 minutos mientras se crea el cluster

#### Paso 3: Crear un usuario de base de datos

1. Ve a **"Database Access"** en el menú izquierdo
2. Haz clic en **"Add New Database User"**
3. Configuración:
   - **Authentication Method:** Password
   - **Username:** `educando_user` (o el que prefieras)
   - **Password:** Genera una contraseña segura (cópiala, la necesitarás)
   - **Database User Privileges:** Selecciona "Read and write to any database"
4. Haz clic en **"Add User"**

⚠️ **IMPORTANTE:** Guarda el usuario y contraseña en un lugar seguro.

#### Paso 4: Permitir acceso desde cualquier IP

1. Ve a **"Network Access"** en el menú izquierdo
2. Haz clic en **"Add IP Address"**
3. Haz clic en **"Allow Access from Anywhere"** (0.0.0.0/0)
   - Esto es necesario porque Render usa IPs dinámicas
4. Haz clic en **"Confirm"**

#### Paso 5: Obtener la Connection String (Cadena de conexión)

1. Ve a **"Database"** en el menú izquierdo
2. En tu cluster, haz clic en **"Connect"**
3. Selecciona **"Connect your application"**
4. En "Driver", selecciona: **Python** y versión **3.12 or later**
5. Copia la **Connection String** que se muestra. Se verá así:
   ```
   mongodb+srv://educando_user:<password>@educando-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **IMPORTANTE:** Reemplaza `<password>` con la contraseña que creaste en el Paso 3
7. **IMPORTANTE:** Agrega el nombre de la base de datos antes de `?`. Ejemplo:
   ```
   mongodb+srv://educando_user:TuPassword123@educando-cluster.xxxxx.mongodb.net/educando_db?retryWrites=true&w=majority
   ```

#### Paso 6: Configurar la variable MONGO_URL en Render

1. Ve a tu dashboard de Render: https://dashboard.render.com
2. Selecciona tu servicio `educando-backend`
3. Ve a la pestaña **"Environment"**
4. Busca la variable `MONGO_URL` o agrégala si no existe:
   - **Key:** `MONGO_URL`
   - **Value:** Pega la connection string que copiaste (con tu contraseña y el nombre de base de datos)
5. Haz clic en **"Save Changes"**

**Ejemplo de MONGO_URL correcto:**
```
mongodb+srv://educando_user:MiPassword123@educando-cluster.abc123.mongodb.net/educando_db?retryWrites=true&w=majority
```

⚠️ **ERRORES COMUNES:**
- ❌ Olvidar reemplazar `<password>` con tu contraseña real
- ❌ Olvidar agregar `/educando_db` antes del `?`
- ❌ No permitir acceso desde cualquier IP en "Network Access"
- ❌ Espacios al inicio o final de la connection string

#### Paso 7: Re-desplegar el backend en Render

1. En Render, ve a tu servicio `educando-backend`
2. Haz clic en **"Manual Deploy"** → **"Deploy latest commit"**
3. Espera que termine el despliegue (1-3 minutos)
4. **Ve a los logs** (pestaña "Logs") y verifica:
   - ✅ `MongoDB connection successful`
   - ✅ `Datos iniciales creados exitosamente`
   - ✅ `Credenciales creadas para 7 usuarios.`

#### Paso 8: Probar el login

1. Ve a tu aplicación en Render (URL del frontend)
2. Intenta iniciar sesión con las credenciales del archivo `USUARIOS_Y_CONTRASEÑAS.txt`
3. Ejemplo de prueba:
   - **Rol:** Profesor (selecciona la pestaña "Profesor")
   - **Email:** `laura.torres@educando.com`
   - **Contraseña:** `Admin2026*LT`
4. Si funciona, verás el dashboard correspondiente

---

### Opción 2: Render Private Services (MongoDB)

Render también ofrece MongoDB privado, pero es de pago:
- Costo: Desde $7/mes
- Ventaja: Todo en Render, más simple
- Desventaja: Más caro que Atlas Free

**Pasos:**
1. En Render dashboard, haz clic en **"New +"**
2. Selecciona **"Private Service"** → **"MongoDB"**
3. Sigue las instrucciones de Render
4. Copia la Connection String interna
5. Agrégala como variable `MONGO_URL` en tu backend

---

## 🔍 VERIFICAR QUE LOS USUARIOS EXISTAN EN LA BASE DE DATOS

### Método 1: Usar MongoDB Compass (GUI - Recomendado)

MongoDB Compass es una aplicación gráfica oficial de MongoDB.

1. **Descargar MongoDB Compass:**
   - Ve a: https://www.mongodb.com/try/download/compass
   - Descarga e instala la versión para tu sistema operativo

2. **Conectar a tu base de datos:**
   - Abre MongoDB Compass
   - En "New Connection", pega tu connection string de Atlas
   - Haz clic en "Connect"

3. **Ver los usuarios:**
   - En el panel izquierdo, expande tu base de datos (`educando_db`)
   - Haz clic en la colección `users`
   - Verás la lista de todos los usuarios creados

4. **Verificar que existen 7 usuarios:**
   - 1 Editor: carlos.mendez@educando.com
   - 2 Administradores: laura.torres@educando.com, roberto.ramirez@educando.com
   - 2 Profesores: diana.silva@educando.com, miguel.castro@educando.com
   - 2 Estudiantes: cédulas 1001234567, 1002345678

### Método 2: Usar mongosh (Línea de comandos)

1. **Instalar mongosh:**
   ```bash
   # En Ubuntu/Debian
   wget -qO- https://www.mongodb.org/static/pgp/server-7.0.asc | sudo tee /etc/apt/trusted.gpg.d/server-7.0.asc
   echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list
   sudo apt-get update
   sudo apt-get install -y mongodb-mongosh

   # En macOS
   brew install mongosh

   # En Windows
   # Descargar desde: https://www.mongodb.com/try/download/shell
   ```

2. **Conectar a la base de datos:**
   ```bash
   mongosh "mongodb+srv://educando_user:TuPassword@educando-cluster.xxxxx.mongodb.net/educando_db"
   ```

3. **Listar todos los usuarios:**
   ```javascript
   db.users.find().pretty()
   ```

4. **Contar usuarios:**
   ```javascript
   db.users.countDocuments()
   // Debe devolver: 7
   ```

5. **Verificar un usuario específico:**
   ```javascript
   // Por email (para profesores/admins/editores)
   db.users.findOne({email: "laura.torres@educando.com"})

   // Por cédula (para estudiantes)
   db.users.findOne({cedula: "1001234567"})
   ```

### Método 3: Usar MongoDB Atlas Web Interface

1. Ve a: https://cloud.mongodb.com
2. Inicia sesión con tu cuenta
3. Selecciona tu cluster
4. Haz clic en **"Browse Collections"**
5. Selecciona la base de datos `educando_db`
6. Haz clic en la colección `users`
7. Verás todos los usuarios listados

---

## 🧪 SCRIPT DE VERIFICACIÓN AUTOMÁTICA

Puedes usar este script para verificar la conexión desde tu computadora local:

```python
# test_mongodb_connection.py
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient

async def test_connection():
    # REEMPLAZA ESTO con tu connection string
    MONGO_URL = "mongodb+srv://educando_user:TuPassword@educando-cluster.xxxxx.mongodb.net/educando_db?retryWrites=true&w=majority"
    
    print("Intentando conectar a MongoDB...")
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        db = client.educando_db
        
        # Probar la conexión
        await db.command('ping')
        print("✅ Conexión exitosa a MongoDB!")
        
        # Contar usuarios
        user_count = await db.users.count_documents({})
        print(f"✅ Usuarios en la base de datos: {user_count}")
        
        if user_count == 0:
            print("⚠️  No hay usuarios en la base de datos. El backend los creará automáticamente al iniciar.")
        elif user_count == 7:
            print("✅ Todos los usuarios iniciales están presentes!")
        else:
            print(f"⚠️  Número inesperado de usuarios: {user_count}")
        
        # Listar usuarios
        print("\nUsuarios encontrados:")
        async for user in db.users.find({}, {"_id": 0, "password_hash": 0}):
            print(f"  - {user.get('name')} ({user.get('role')}) - {user.get('email') or user.get('cedula')}")
        
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        print("\nVerifica:")
        print("  1. Que la connection string sea correcta")
        print("  2. Que hayas reemplazado <password> con tu contraseña real")
        print("  3. Que hayas permitido acceso desde cualquier IP en Atlas")
        print("  4. Que tu conexión a internet funcione")

if __name__ == "__main__":
    asyncio.run(test_connection())
```

**Uso:**
```bash
# Instalar dependencias
pip install motor

# Ejecutar el script
python test_mongodb_connection.py
```

---

## 📋 CHECKLIST: ¿TODO ESTÁ CONFIGURADO CORRECTAMENTE?

- [ ] ✅ Creé una cuenta en MongoDB Atlas
- [ ] ✅ Creé un cluster gratuito (M0)
- [ ] ✅ Creé un usuario de base de datos con contraseña
- [ ] ✅ Permití acceso desde cualquier IP (0.0.0.0/0)
- [ ] ✅ Copié la connection string correctamente
- [ ] ✅ Reemplacé `<password>` con mi contraseña real
- [ ] ✅ Agregué `/educando_db` antes del `?` en la connection string
- [ ] ✅ Configuré la variable `MONGO_URL` en Render
- [ ] ✅ Re-desplegué el backend en Render
- [ ] ✅ Verifiqué los logs y vi "MongoDB connection successful"
- [ ] ✅ Probé iniciar sesión con las credenciales del archivo USUARIOS_Y_CONTRASEÑAS.txt

---

## 🆘 SOLUCIÓN DE PROBLEMAS

### Error: "ServerSelectionTimeoutError"

**Causa:** No se puede conectar a MongoDB
**Soluciones:**
1. Verifica que el cluster de Atlas esté activo (no en pausa)
2. Verifica la connection string (sin espacios, con contraseña correcta)
3. Verifica que permitiste acceso desde cualquier IP en Network Access
4. Espera 2-3 minutos después de crear el cluster

### Error: "Authentication failed"

**Causa:** Usuario o contraseña incorrecta en la connection string
**Soluciones:**
1. Verifica que reemplazaste `<password>` correctamente
2. Si la contraseña tiene caracteres especiales, encódalos:
   - `@` → `%40`
   - `:` → `%3A`
   - `/` → `%2F`
   - `?` → `%3F`
   - Ejemplo: `Pass@123` → `Pass%40123`
3. O genera una nueva contraseña sin caracteres especiales

### Error: "Credenciales incorrectas" en el login

**Causa 1:** MongoDB no está conectado
- Verifica los logs del backend en Render
- Debe decir "MongoDB connection successful"

**Causa 2:** Los usuarios no se crearon
- Verifica que el log diga "Datos iniciales creados exitosamente"
- Conecta a MongoDB con Compass y verifica que existan usuarios

**Causa 3:** Estás usando el rol incorrecto
- Estudiantes: Usa la pestaña "ESTUDIANTE" e ingresa la cédula
- Profesores/Admins/Editores: Usa la pestaña "PROFESOR" e ingresa el email

**Causa 4:** Contraseña incorrecta
- Verifica las contraseñas en `USUARIOS_Y_CONTRASEÑAS.txt`
- Las contraseñas distinguen entre mayúsculas y minúsculas

### Los logs dicen "MongoDB connection successful" pero el login no funciona

1. Verifica que el frontend esté apuntando al backend correcto:
   - En Render, ve al servicio `educando-frontend`
   - Verifica la variable `REACT_APP_BACKEND_URL`
   - Debe ser la URL del backend (ej: `https://educando-backend.onrender.com`)

2. Verifica que el backend esté respondiendo:
   - Ve a: `https://tu-backend.onrender.com/api/health`
   - Debe devolver: `{"status": "healthy"}`

3. Abre la consola del navegador (F12) y verifica errores:
   - Ve a la pestaña "Network" al intentar iniciar sesión
   - Busca errores de CORS o 500

---

## 📚 RECURSOS ADICIONALES

- **MongoDB Atlas Docs:** https://www.mongodb.com/docs/atlas/
- **Render Docs:** https://render.com/docs
- **Guía de despliegue completa:** Ver archivo `DESPLIEGUE.md`
- **Credenciales de usuarios:** Ver archivo `USUARIOS_Y_CONTRASEÑAS.txt`
- **Código de autenticación:** `backend/server.py` líneas 605-683

---

## 🔧 VARIABLES DE ENTORNO ESENCIALES EN RENDER

Para asegurar persistencia y comportamiento correcto en producción, configura estas variables de entorno en Render:

| Variable | Descripción | Valor recomendado (producción) |
|---|---|---|
| `MONGO_URL` | URL de conexión a MongoDB Atlas | `mongodb+srv://usuario:password@cluster.mongodb.net/WebApp?retryWrites=true&w=majority` |
| `DB_NAME` | Nombre de la base de datos | `WebApp` (o el nombre que uses en tu Atlas) |
| `JWT_SECRET` | Clave secreta para JWT (tokens de sesión) | Una cadena aleatoria larga y segura |
| `CREATE_SEED_USERS` | Controla si se crean usuarios semilla al iniciar | `false` — **desactivar en producción** para evitar que los usuarios semilla se creen automáticamente en cada reinicio del servicio |
| `ALLOW_USER_RESET` | Permite el endpoint `/api/reset-users` | `false` — desactivar en producción |
| `RESET_USERS` | Elimina todos los usuarios al iniciar | `false` (nunca en producción) |
| `PASSWORD_STORAGE_MODE` | Modo de almacenamiento de contraseñas | `bcrypt` |

### ⚠️ Notas importantes sobre persistencia de datos

- **`MONGO_URL`** y **`DB_NAME`** deben apuntar siempre a la misma base de datos. Si cambias estas variables, los usuarios y datos creados anteriormente NO estarán disponibles.
- Si ves que se crean usuarios semilla al reiniciar el servicio, verifica que `CREATE_SEED_USERS=false` esté configurado.
- El endpoint `/api/reset-users` es destructivo (elimina todos los usuarios). Desactívalo en producción con `ALLOW_USER_RESET=false`.

---



**Tu problema:** Las credenciales no funcionan porque MongoDB no está conectado.

**La solución en 5 pasos:**
1. Crear cuenta en MongoDB Atlas (gratis)
2. Crear un cluster gratuito (M0)
3. Crear usuario y permitir acceso desde cualquier IP
4. Copiar la connection string y configurar `MONGO_URL` en Render
5. Re-desplegar el backend y verificar los logs

**Después:** Los usuarios se crearán automáticamente al iniciar el backend.

**Credenciales de prueba:**
- Admin: `laura.torres@educando.com` / Ver USUARIOS_Y_CONTRASEÑAS.txt
- Estudiante: Cédula `1001234567` / Ver USUARIOS_Y_CONTRASEÑAS.txt

---

*Última actualización: 2026-02-18*
