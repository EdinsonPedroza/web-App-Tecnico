# ✅ SOLUCIÓN COMPLETA: Credenciales y MongoDB en Render

## 📍 TUS PREGUNTAS RESPONDIDAS

### ❓ 1. ¿Dónde se almacenan los usuarios?

**RESPUESTA:** Los usuarios se almacenan en **MongoDB**, una base de datos NoSQL.

- **Base de datos:** `educando_db`
- **Colección:** `users`
- **Ubicación física:** MongoDB Atlas (nube) o servidor MongoDB local
- **Código fuente:** `backend/server.py` (líneas 124-262 para creación, 605-683 para autenticación)

**Total de usuarios creados automáticamente:** 7
- 1 Editor
- 2 Administradores
- 2 Profesores
- 2 Estudiantes

### ❓ 2. ¿Por qué las credenciales no funcionan?

**RESPUESTA:** La causa MÁS PROBABLE es que **MongoDB NO está conectado en Render**.

Sin MongoDB conectado:
- ❌ No se pueden almacenar usuarios
- ❌ No se pueden verificar credenciales
- ❌ El login falla con "Credenciales incorrectas"

### ❓ 3. ¿Debería haber una base de datos conectada a Render?

**RESPUESTA:** **SÍ, ABSOLUTAMENTE.** Pero hay algo importante que debes saber:

⚠️ **Render NO incluye MongoDB automáticamente.**

A diferencia de un despliegue local con Docker, donde MongoDB se inicia automáticamente, en Render debes:
1. Crear una base de datos MongoDB por separado
2. Configurar la variable `MONGO_URL` manualmente
3. Re-desplegar el backend

### ❓ 4. ¿Cómo verifico que todo esté bien?

**RESPUESTA:** Hay 4 formas de verificar:

1. **Logs del backend en Render** (Más rápido)
2. **MongoDB Compass** (Interfaz gráfica)
3. **Script de verificación** (Automatizado)
4. **MongoDB Atlas web interface** (Desde el navegador)

Ver detalles más abajo ⬇️

---

## 🎯 SOLUCIÓN EN 3 PASOS

### PASO 1: Configurar MongoDB Atlas (15 minutos)

MongoDB Atlas es el servicio oficial de MongoDB en la nube con plan gratuito.

**Guía completa:** [RENDER_MONGODB_SETUP.md](RENDER_MONGODB_SETUP.md)

**Resumen rápido:**
```
1. Cuenta en MongoDB Atlas → https://www.mongodb.com/cloud/atlas/register
2. Crear cluster gratuito (M0) → 512MB gratis
3. Crear usuario de BD → Usuario + contraseña
4. Network Access → 0.0.0.0/0 (permitir todo)
5. Copiar connection string → Reemplazar <password>
6. Agregar /educando_db antes del ?
```

### PASO 2: Configurar MONGO_URL en Render (2 minutos)

```
1. Render Dashboard → https://dashboard.render.com
2. Seleccionar servicio: educando-backend
3. Pestaña: Environment
4. Agregar variable:
   Key: MONGO_URL
   Value: mongodb+srv://usuario:contraseña@cluster.mongodb.net/educando_db?...
5. Save Changes
6. Manual Deploy → Deploy latest commit
7. Esperar 2-3 minutos
```

### PASO 3: Verificar que funcione (1 minuto)

```
1. Render → educando-backend → Logs
2. Buscar:
   ✅ "MongoDB connection successful"
   ✅ "Datos iniciales creados exitosamente"
   ✅ "Credenciales creadas para 7 usuarios"
3. Probar login con credenciales de USUARIOS_Y_CONTRASEÑAS.txt
```

---

## 📚 DOCUMENTACIÓN CREADA PARA TI

He creado **7 archivos de documentación** para ayudarte:

### 1. 📖 RENDER_MONGODB_SETUP.md
**Guía completa paso a paso (400+ líneas)**
- Cómo crear cuenta en MongoDB Atlas
- Configuración detallada del cluster
- Obtener connection string
- Configurar Render
- Solución de problemas
- Scripts de verificación

**Úsalo cuando:** Necesites configurar MongoDB desde cero

### 2. 📋 RESUMEN_USUARIOS_Y_MONGODB.md
**Resumen ejecutivo con checklist**
- Respuestas directas a tus preguntas
- Diagnóstico rápido
- Checklist completo
- Problemas comunes

**Úsalo cuando:** Necesites una visión general rápida

### 3. 📇 TARJETA_REFERENCIA_MONGODB.md
**Referencia rápida de 1 página (para imprimir)**
- Configuración en 5 pasos
- Comandos útiles
- Errores comunes
- Diagnóstico en 30 segundos

**Úsalo cuando:** Necesites consultar algo rápido

### 4. 🔧 backend/verify_mongodb.py
**Script de verificación automática**
- Verifica conexión a MongoDB
- Lista usuarios y colecciones
- Diagnóstico detallado
- Mensajes de error claros

**Úsalo cuando:** Quieras verificar tu connection string

### 5. ⚙️ render.yaml (actualizado)
**Configuración de Render con comentarios**
- Explica por qué MongoDB debe configurarse manualmente
- Ejemplos de connection strings
- Enlaces a documentación

**Úsalo cuando:** Despliegues con Render Blueprint

### 6. 📘 README.md (actualizado)
**Sección de troubleshooting agregada**
- Problemas con autenticación en Render
- Cómo usar el script de verificación
- Enlaces a guías completas

**Úsalo cuando:** Busques ayuda en el README

### 7. 📚 DESPLIEGUE.md (actualizado)
**Sección de Render mejorada**
- Instrucciones claras sobre MongoDB
- Recomendación de MongoDB Atlas
- Referencias a nuevas guías

**Úsalo cuando:** Sigas el tutorial de despliegue

---

## 🔍 CÓMO VERIFICAR QUE TODO FUNCIONE

### Método 1: Logs de Render (El más rápido) ⭐

```
1. https://dashboard.render.com
2. educando-backend → Logs
3. Buscar estos mensajes:
```

**✅ Si está bien configurado:**
```
INFO - Starting application initialization...
INFO - Connecting to MongoDB at: cloud/remote
INFO - MongoDB connection successful
INFO - MongoDB client initialized for database: educando_db
INFO - Datos iniciales creados exitosamente
INFO - Credenciales creadas para 7 usuarios.
INFO - Ver archivo USUARIOS_Y_CONTRASEÑAS.txt para detalles de acceso.
INFO - Application startup completed successfully
```

**❌ Si MongoDB NO está conectado:**
```
ERROR - Startup failed: ServerSelectionTimeoutError...
ERROR - MongoDB connection failed. Please check your MONGO_URL environment variable.
ERROR - Common causes: invalid credentials, IP not whitelisted in MongoDB Atlas...
WARNING - Application started WITHOUT database connection.
WARNING - API endpoints requiring MongoDB will not work until the connection is restored.
```

### Método 2: Script de verificación

Desde tu computadora:
```bash
# Instalar dependencias
pip install motor python-dotenv

# Ejecutar verificación
cd backend
python verify_mongodb.py "mongodb+srv://user:pass@cluster.mongodb.net/educando_db"
```

Salida esperada:
```
✅ ¡Conexión exitosa a MongoDB!
✅ Usuarios en la base de datos: 7
✅ ¡Perfecto! Los 7 usuarios iniciales están presentes.

📋 Lista de usuarios:
  [✓] Laura Torres           | admin        | laura.torres@educando.com
  [✓] Roberto Ramirez        | admin        | roberto.ramirez@educando.com
  [✓] Diana Silva            | profesor     | diana.silva@educando.com
  [✓] Miguel Castro          | profesor     | miguel.castro@educando.com
  [✓] Carlos Mendez          | editor       | carlos.mendez@educando.com
  [✓] Sofía Morales          | estudiante   | 1001234567
  [✓] Andrés Lopez           | estudiante   | 1002345678
```

### Método 3: MongoDB Compass (GUI)

1. Descargar: https://www.mongodb.com/try/download/compass
2. Instalar y abrir
3. Conectar con tu connection string
4. Navegar a: `educando_db` → colección `users`
5. Deberías ver **7 usuarios**

### Método 4: Probar el login

1. Ve a tu aplicación en Render (URL del frontend)
2. Selecciona pestaña **"PROFESOR"**
3. Email: `laura.torres@educando.com`
4. Contraseña: Ver `USUARIOS_Y_CONTRASEÑAS.txt`
5. Haz clic en "Ingresar"

**✅ Si funciona:** Verás el dashboard de administrador  
**❌ Si no funciona:** MongoDB no está conectado → Ver logs del backend

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: "ServerSelectionTimeoutError"

**Síntoma:** Backend no puede conectarse a MongoDB

**Causas y soluciones:**
1. ❌ Cluster en pausa → Esperar que se active (1-2 minutos)
2. ❌ IP no permitida → Network Access → 0.0.0.0/0
3. ❌ Connection string incorrecta → Verificar formato
4. ❌ Cluster recién creado → Esperar 2-3 minutos

### Problema 2: "Authentication failed"

**Síntoma:** Error de autenticación en connection string

**Causas y soluciones:**
1. ❌ No reemplazaste `<password>` → Reemplazar con contraseña real
2. ❌ Contraseña con caracteres especiales → Codificar (@→%40, :→%3A) o usar contraseña simple
3. ❌ Usuario no existe → Crear usuario en Database Access

### Problema 3: "Credenciales incorrectas" en login

**Síntoma:** Login falla con credenciales correctas

**Diagnóstico:**
```
1. ¿MongoDB conectado?
   → Logs: "MongoDB connection successful" ✅
   → Si NO: Configurar MONGO_URL

2. ¿Usuarios creados?
   → Logs: "Credenciales creadas para 7 usuarios" ✅
   → Si NO: Re-desplegar backend

3. ¿Rol correcto?
   → Estudiantes: Pestaña ESTUDIANTE + cédula
   → Otros: Pestaña PROFESOR + email

4. ¿Contraseña correcta?
   → Ver USUARIOS_Y_CONTRASEÑAS.txt
   → Distingue mayúsculas/minúsculas
```

### Problema 4: Frontend no conecta con backend

**Síntoma:** Errores de red en la consola del navegador

**Solución:**
```
1. Render → educando-frontend → Environment
2. Verificar REACT_APP_BACKEND_URL
3. Debe ser: https://educando-backend.onrender.com (tu URL)
4. Save Changes
5. Re-desplegar frontend
```

---

## 👥 CREDENCIALES DE USUARIOS

**Archivo completo:** [USUARIOS_Y_CONTRASEÑAS.txt](USUARIOS_Y_CONTRASEÑAS.txt)

### Usuarios de prueba (usar pestaña "PROFESOR"):

```
🔑 Admin 1:
   Email: laura.torres@educando.com
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt

🔑 Admin 2:
   Email: roberto.ramirez@educando.com
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt

🔑 Profesor 1:
   Email: diana.silva@educando.com
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt

🔑 Editor:
   Email: carlos.mendez@educando.com
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt
```

### Estudiantes (usar pestaña "ESTUDIANTE"):

```
🎓 Estudiante 1:
   Cédula: 1001234567
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt

🎓 Estudiante 2:
   Cédula: 1002345678
   Pass: Ver USUARIOS_Y_CONTRASEÑAS.txt
```

**⚠️ IMPORTANTE:** 
- Admins, Profesores y Editores usan la pestaña **"PROFESOR"**
- Estudiantes usan la pestaña **"ESTUDIANTE"**

---

## 📊 RESUMEN DE ARCHIVOS IMPORTANTES

```
┌─ Documentación ─────────────────────────────────────────┐
│ RENDER_MONGODB_SETUP.md         → Guía completa        │
│ RESUMEN_USUARIOS_Y_MONGODB.md   → Resumen ejecutivo    │
│ TARJETA_REFERENCIA_MONGODB.md   → Referencia rápida    │
│ USUARIOS_Y_CONTRASEÑAS.txt      → Credenciales         │
└─────────────────────────────────────────────────────────┘

┌─ Herramientas ──────────────────────────────────────────┐
│ backend/verify_mongodb.py        → Script verificación │
└─────────────────────────────────────────────────────────┘

┌─ Configuración ─────────────────────────────────────────┐
│ render.yaml                      → Config Render       │
│ backend/.env                     → Variables entorno   │
│ backend/server.py                → Código backend      │
└─────────────────────────────────────────────────────────┘
```

---

## 🎯 CHECKLIST FINAL

Marca cada paso cuando lo completes:

### Configuración de MongoDB Atlas
- [ ] ✅ Creé cuenta en MongoDB Atlas
- [ ] ✅ Creé cluster M0 (gratis, 512MB)
- [ ] ✅ Creé usuario de base de datos con contraseña
- [ ] ✅ Permití acceso desde 0.0.0.0/0 en Network Access
- [ ] ✅ Copié connection string
- [ ] ✅ Reemplacé `<password>` con mi contraseña real
- [ ] ✅ Agregué `/educando_db` antes del `?`

### Configuración en Render
- [ ] ✅ Fui a Render Dashboard → educando-backend → Environment
- [ ] ✅ Agregué/actualicé variable `MONGO_URL`
- [ ] ✅ Guardé cambios (Save Changes)
- [ ] ✅ Re-desplegué: Manual Deploy → Deploy latest commit
- [ ] ✅ Esperé 2-3 minutos que termine el despliegue

### Verificación
- [ ] ✅ Revisé los logs del backend en Render
- [ ] ✅ Vi mensaje: "MongoDB connection successful"
- [ ] ✅ Vi mensaje: "Datos iniciales creados exitosamente"
- [ ] ✅ Vi mensaje: "Credenciales creadas para 7 usuarios"
- [ ] ✅ Probé iniciar sesión con laura.torres@educando.com
- [ ] ✅ El login funcionó y entré al dashboard
- [ ] 🎉 **¡TODO FUNCIONA!**

---

## 🔗 ENLACES ÚTILES

```
MongoDB Atlas:         https://www.mongodb.com/cloud/atlas
Render Dashboard:      https://dashboard.render.com
MongoDB Compass:       https://www.mongodb.com/try/download/compass
Tu Repositorio:        https://github.com/EdinsonPedroza/web-App-Tecnico
```

---

## 💡 PRÓXIMOS PASOS

Una vez que MongoDB esté funcionando:

1. **Cambiar contraseñas de producción**
   - Ver archivo `USUARIOS_Y_CONTRASEÑAS.txt` sección de seguridad
   - Cambiar todas las contraseñas desde el panel de administración

2. **Configurar dominio personalizado (opcional)**
   - Ver `DESPLIEGUE.md` sección "Configurar un Dominio Personalizado"

3. **Monitorear uso de MongoDB Atlas**
   - MongoDB Atlas → Metrics
   - El plan gratuito tiene 512MB de almacenamiento
   - Suficiente para ~500-1000 usuarios

4. **Backup de datos (recomendado)**
   - MongoDB Atlas tiene backups automáticos en planes pagos
   - Para plan gratuito: Usar `mongodump` periódicamente

---

## 🆘 ¿NECESITAS MÁS AYUDA?

Si después de seguir esta guía sigues teniendo problemas:

1. **Verifica los logs del backend:**
   - Render → educando-backend → Logs
   - Copia el mensaje de error completo

2. **Prueba el script de verificación:**
   - `python backend/verify_mongodb.py "tu_connection_string"`
   - Copia la salida completa

3. **Verifica la connection string:**
   - ¿Reemplazaste `<password>`? ✓
   - ¿Agregaste `/educando_db`? ✓
   - ¿Sin espacios al inicio/final? ✓

4. **Consulta las guías:**
   - `RENDER_MONGODB_SETUP.md` - Guía completa paso a paso
   - `TARJETA_REFERENCIA_MONGODB.md` - Diagnóstico rápido

---

## ✅ CONCLUSIÓN

**Tu pregunta:** ¿Dónde se almacenan los usuarios?  
**Respuesta:** En MongoDB, colección `users` de la base de datos `educando_db`

**Tu problema:** Las credenciales no funcionan  
**Causa:** MongoDB no está conectado en Render  
**Solución:** Configurar MongoDB Atlas (gratis) y agregar `MONGO_URL` en Render

**Tiempo total:** 15-20 minutos

**Archivos para ayudarte:**
- 📖 `RENDER_MONGODB_SETUP.md` - Guía completa
- 📋 `RESUMEN_USUARIOS_Y_MONGODB.md` - Este archivo
- 📇 `TARJETA_REFERENCIA_MONGODB.md` - Referencia rápida
- 🔧 `backend/verify_mongodb.py` - Script de verificación
- 🔐 `USUARIOS_Y_CONTRASEÑAS.txt` - Credenciales

**Siguiente paso:** Abre `RENDER_MONGODB_SETUP.md` y sigue los pasos.

---

*¡Éxito con tu despliegue! 🚀*  
*Última actualización: 2026-02-18*
