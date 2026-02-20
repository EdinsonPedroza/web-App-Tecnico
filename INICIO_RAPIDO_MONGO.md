# 🚀 INICIO RÁPIDO - Si las Credenciales NO Funcionan

## ❌ PROBLEMA: "Las credenciales no sirven"

### 🎯 DIAGNÓSTICO EN 30 SEGUNDOS

**1. Ve a Render:**
```
https://dashboard.render.com
→ Selecciona: educando-backend
→ Pestaña: Logs
```

**2. Busca esta línea:**
```
"MongoDB connection successful"
```

**3. ¿La encontraste?**

✅ **SÍ** → MongoDB está conectado, ve a [Sección B](#sección-b-mongodb-conectado-pero-login-falla)

❌ **NO** → MongoDB NO está conectado, ve a [Sección A](#sección-a-mongodb-no-conectado)

---

## 🔴 SECCIÓN A: MongoDB NO Conectado

Si NO viste el mensaje "MongoDB connection successful", sigue estos pasos:

### Paso 1: Crear MongoDB Atlas (10 minutos)

1. **Crear cuenta:**
   ```
   https://www.mongodb.com/cloud/atlas/register
   → Crear cuenta gratis (puedes usar Google/GitHub)
   ```

2. **Crear cluster:**
   ```
   → Build a Database
   → M0 FREE (512MB gratis)
   → Proveedor: AWS
   → Región: us-east-1 (o la más cercana)
   → Cluster Name: educando-cluster
   → Create
   → Esperar 2-3 minutos
   ```

3. **Crear usuario:**
   ```
   → Database Access (menú izquierdo)
   → Add New Database User
   → Username: educando_user
   → Password: [Generar una segura, CÓPIALE!]
   → Database User Privileges: Read and write to any database
   → Add User
   ```

4. **Permitir acceso:**
   ```
   → Network Access (menú izquierdo)
   → Add IP Address
   → Allow Access from Anywhere (0.0.0.0/0)
   → Confirm
   ```

5. **Copiar connection string:**
   ```
   → Database (menú izquierdo)
   → En tu cluster, clic en "Connect"
   → Connect your application
   → Driver: Python / 3.12 or later
   → COPIAR la connection string
   ```

   Se verá así:
   ```
   mongodb+srv://educando_user:<password>@educando-cluster.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```

6. **Editar connection string:**
   
   ⚠️ **MUY IMPORTANTE - HAZ ESTOS 2 CAMBIOS:**
   
   **Cambio 1:** Reemplaza `<password>` con tu contraseña real
   
   **Cambio 2:** Agrega `/educando_db` antes del `?`
   
   **ANTES:**
   ```
   mongodb+srv://educando_user:<password>@cluster.xxxxx.mongodb.net/?retryWrites=true
   ```
   
   **DESPUÉS:**
   ```
   mongodb+srv://educando_user:MiPassword123@cluster.xxxxx.mongodb.net/educando_db?retryWrites=true
   ```
   ↑ Contraseña real          ↑ Nombre de base de datos

### Paso 2: Configurar en Render (2 minutos)

1. **Ve a Render:**
   ```
   https://dashboard.render.com
   → Selecciona: educando-backend
   → Pestaña: Environment
   ```

2. **Busca la variable `MONGO_URL`:**
   
   **Si NO existe:**
   ```
   → Clic en "Add Environment Variable"
   → Key: MONGO_URL
   → Value: [Pega tu connection string editada]
   → Save Changes
   ```
   
   **Si ya existe:**
   ```
   → Clic en el ícono de editar (lápiz)
   → Reemplaza el valor con tu connection string
   → Save Changes
   ```

3. **Re-desplegar:**
   ```
   → Pestaña: Manual Deploy
   → Deploy latest commit
   → Esperar 2-3 minutos
   ```

### Paso 3: Verificar que Funcionó (1 minuto)

1. **Ver los logs:**
   ```
   → Pestaña: Logs
   → Buscar:
     ✅ "MongoDB connection successful"
     ✅ "Datos iniciales creados exitosamente"
     ✅ "Credenciales creadas para 7 usuarios"
   ```

2. **Probar login:**
   ```
   → Ve a tu aplicación
   → Pestaña: PROFESOR
   → Email: laura.torres@educando.com
   → Contraseña: Admin2026*LT
   → Clic en "Ingresar"
   ```

✅ **¡LISTO! Debería funcionar ahora.**

---

## 🟢 SECCIÓN B: MongoDB Conectado pero Login Falla

Si viste "MongoDB connection successful" pero el login no funciona:

### Verificación 1: ¿Los usuarios se crearon?

**En los logs de Render, busca:**
```
"Credenciales creadas para 7 usuarios"
```

❌ **NO lo veo:**
```
→ Manual Deploy → Deploy latest commit
→ Esperar 2-3 minutos
→ Revisar logs nuevamente
```

✅ **SÍ lo veo:** Continúa a Verificación 2

### Verificación 2: ¿Estás usando el rol correcto?

**Para ESTUDIANTES:**
```
→ Pestaña: ESTUDIANTE (NO Profesor)
→ Usuario: 1001234567 (SIN puntos ni guiones)
→ Contraseña: Estud2026*SM
```

**Para PROFESORES/ADMINS/EDITORES:**
```
→ Pestaña: PROFESOR (NO Estudiante)
→ Usuario: laura.torres@educando.com (email completo)
→ Contraseña: Admin2026*LT
```

⚠️ **IMPORTANTE:** Los admins y editores también usan la pestaña "PROFESOR"

### Verificación 3: ¿La contraseña es correcta?

Las contraseñas distinguen MAYÚSCULAS y minúsculas.

**Prueba con estos usuarios de prueba:**

| Rol | Pestaña | Usuario | Contraseña |
|-----|---------|---------|------------|
| Admin | PROFESOR | laura.torres@educando.com | Admin2026*LT |
| Admin | PROFESOR | roberto.ramirez@educando.com | Admin2026*RR |
| Profesor | PROFESOR | diana.silva@educando.com | Profe2026*DS |
| Estudiante | ESTUDIANTE | 1001234567 | Estud2026*SM |
| Estudiante | ESTUDIANTE | 1002345678 | Estud2026*AL |

⚠️ Copia y pega la contraseña exactamente como está escrita.

### Verificación 4: ¿El frontend conecta con el backend?

1. **Verifica la URL del backend:**
   ```
   → Render → educando-frontend → Environment
   → Busca: REACT_APP_BACKEND_URL
   → Debe ser algo como: https://educando-backend.onrender.com
   ```

2. **Verifica que el backend responda:**
   ```
   Abre en tu navegador:
   https://TU-BACKEND.onrender.com/api/health
   
   Debe devolver:
   {"status": "healthy"}
   ```

3. **Revisa la consola del navegador:**
   ```
   → Abre tu aplicación
   → Presiona F12 (abre DevTools)
   → Pestaña: Console
   → Intenta hacer login
   → ¿Ves errores?
   ```

---

## 🔍 VER QUÉ HAY EN MONGODB

Si quieres ver exactamente qué usuarios existen en tu base de datos:

### Opción 1: MongoDB Compass (Más Fácil)

1. **Descargar:**
   ```
   https://www.mongodb.com/try/download/compass
   → Descargar para tu sistema operativo
   → Instalar
   ```

2. **Conectar:**
   ```
   → Abrir MongoDB Compass
   → Pegar tu connection string
   → Connect
   ```

3. **Ver usuarios:**
   ```
   → Panel izquierdo: educando_db
   → Colección: users
   → Debes ver 7 usuarios:
     - 1 Editor
     - 2 Admins
     - 2 Profesores
     - 2 Estudiantes
   ```

### Opción 2: MongoDB Atlas Web

1. **Iniciar sesión:**
   ```
   https://cloud.mongodb.com
   → Iniciar sesión
   ```

2. **Ver datos:**
   ```
   → Tu cluster → Browse Collections
   → educando_db → users
   → Verás los 7 usuarios
   ```

### Opción 3: Script Automático

```bash
# Desde el directorio del proyecto
cd backend
pip install motor python-dotenv

# Ejecutar (reemplaza con tu connection string)
python verify_mongodb.py "mongodb+srv://usuario:pass@cluster.mongodb.net/educando_db"
```

**Salida esperada:**
```
✅ ¡Conexión exitosa a MongoDB!
✅ ¡Perfecto! Los 7 usuarios iniciales están presentes.

📋 Lista de usuarios:
   [✓] Laura Torres             | admin        | laura.torres@educando.com
   [✓] Roberto Ramirez          | admin        | roberto.ramirez@educando.com
   [✓] Carlos Mendez            | editor       | carlos.mendez@educando.com
   [✓] Diana Silva              | profesor     | diana.silva@educando.com
   [✓] Miguel Castro            | profesor     | miguel.castro@educando.com
   [✓] Sofía Morales            | estudiante   | 1001234567
   [✓] Andrés Lopez             | estudiante   | 1002345678
```

---

## 🆘 ERRORES COMUNES

### Error: "ServerSelectionTimeoutError"
```
Causa: No puede conectar a MongoDB
Solución:
1. Verifica Network Access en Atlas (0.0.0.0/0)
2. Verifica que el cluster esté activo
3. Espera 2-3 minutos si acabas de crearlo
```

### Error: "Authentication failed"
```
Causa: Usuario o contraseña incorrectos en connection string
Solución:
1. Verifica que reemplazaste <password> con tu contraseña real
2. Si tu contraseña tiene @ o :, crea un nuevo usuario con contraseña simple
```

### Error: "Credenciales incorrectas" en login
```
Causa más común: Pestaña incorrecta
Solución:
1. Estudiantes → Pestaña ESTUDIANTE + cédula
2. Otros roles → Pestaña PROFESOR + email
```

### No veo datos en MongoDB
```
Causa: Los datos no se crearon
Solución:
1. Render → educando-backend → Manual Deploy
2. Espera 2-3 minutos
3. Verifica logs: "Credenciales creadas para 7 usuarios"
```

---

## 📋 CHECKLIST RÁPIDO

Usa esto para verificar que todo esté configurado:

```
MONGODB ATLAS:
[ ] Creé cuenta
[ ] Creé cluster M0 (gratis)
[ ] Creé usuario de base de datos
[ ] Permití 0.0.0.0/0 en Network Access
[ ] Copié connection string
[ ] Reemplacé <password>
[ ] Agregué /educando_db antes del ?

RENDER:
[ ] Configuré MONGO_URL en backend
[ ] Guardé los cambios
[ ] Re-desplegué el backend
[ ] Esperé 2-3 minutos

VERIFICACIÓN:
[ ] Logs dicen "MongoDB connection successful"
[ ] Logs dicen "Credenciales creadas para 7 usuarios"
[ ] Probé login con laura.torres@educando.com
[ ] Login funcionó ✅
```

---

## 📚 DOCUMENTACIÓN COMPLETA

Si necesitas más detalles, consulta estos archivos:

```
QUE_VER_EN_MONGO.md              → Guía visual completa de qué ver en MongoDB
RENDER_MONGODB_SETUP.md          → Guía paso a paso de configuración
USUARIOS_Y_CONTRASEÑAS.txt       → Lista completa de credenciales
TARJETA_REFERENCIA_MONGODB.md    → Referencia rápida
RESUMEN_USUARIOS_Y_MONGODB.md    → Resumen ejecutivo
```

---

## 💡 TIP FINAL

**Si sigues teniendo problemas:**

1. Abre el archivo `QUE_VER_EN_MONGO.md` para una guía visual completa
2. Comparte los logs del backend (últimas 50 líneas)
3. Comparte qué ves en MongoDB Compass

Con esta información podremos ayudarte exactamente.

---

*Esta guía responde: "POR FAVOR YA NO SÉ QUÉ HACER, LAS CREDENCIALES NO SIRVEN"*
*Última actualización: 2026-02-18*
